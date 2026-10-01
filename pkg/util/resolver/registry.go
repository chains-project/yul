package resolver

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"maps"
	"net/http"
	"net/url"
	"strings"
	"sync"

	"github.com/git-pkgs/purl"
	"github.com/git-pkgs/vers"
)

// userAgent identifies yul to registries; crates.io requires one that names
// the client and how to reach its maintainers.
const userAgent = "yul (+https://github.com/chains-project/yul)"

// maxConcurrent caps in-flight registry requests per LatestVersions call.
const maxConcurrent = 16

// registry looks up a package's latest stable release straight from the
// registry that publishes it. name is the purl's full name (e.g.
// "@scope/pkg" for npm, "group:artifact" for Maven).
type registry struct {
	baseURL string
	latest  func(ctx context.Context, c *http.Client, baseURL, name string) (string, error)
}

// registries maps a purl type to its registry. Each uses whatever the
// registry itself publishes as its latest stable release, so yul agrees
// with what a user sees on the registry's own site. Maven reads
// maven-metadata.xml from Maven Central rather than search.maven.org's
// search API, which returned unreliable results.
var registries = map[string]registry{
	"npm":    {"https://registry.npmjs.org", npmLatest},       // e.g. https://registry.npmjs.org/-/package/react/dist-tags
	"pypi":   {"https://pypi.org", pypiLatest},                // e.g. https://pypi.org/pypi/requests/json
	"cargo":  {"https://crates.io", cargoLatest},              // e.g. https://crates.io/api/v1/crates/serde
	"golang": {"https://proxy.golang.org", goLatest},          // e.g. https://proxy.golang.org/github.com/!burnt!sushi/toml/@latest
	"maven":  {"https://repo1.maven.org/maven2", mavenLatest}, // e.g. https://repo1.maven.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
}

// RegistryResolver resolves latest versions by querying each package's
// registry directly instead of a mirror such as ecosyste.ms, which syncs on
// its own schedule and can lag upstream by days. Purl types it has no
// registry for, and lookups that fail (registry down, rate limited, timed
// out, or unknown package), are passed to Fallback.
type RegistryResolver struct {
	Fallback Resolver

	// Client is the HTTP client to use; nil means http.DefaultClient.
	Client *http.Client
}

func (r *RegistryResolver) LatestVersions(ctx context.Context, purls []string) (map[string]string, error) {
	fetchCtx, cancel := context.WithTimeout(ctx, defaultTimeout)
	defer cancel()

	client := r.Client
	if client == nil {
		client = http.DefaultClient
	}

	var (
		mu       sync.Mutex
		wg       sync.WaitGroup
		sem      = make(chan struct{}, maxConcurrent)
		latest   = make(map[string]string, len(purls))
		fallback []string
	)
	for _, p := range purls {
		parsed, err := purl.Parse(p)
		if err != nil {
			continue
		}
		reg, ok := registries[parsed.Type]
		if !ok {
			fallback = append(fallback, p)
			continue
		}
		wg.Go(func() {
			sem <- struct{}{}
			defer func() { <-sem }()
			v, err := reg.latest(fetchCtx, client, reg.baseURL, fullName(p, parsed))
			mu.Lock()
			defer mu.Unlock()
			if err != nil || v == "" {
				fallback = append(fallback, p)
				return
			}
			latest[p] = v
		})
	}
	wg.Wait()

	if len(fallback) > 0 && r.Fallback != nil {
		got, err := r.Fallback.LatestVersions(ctx, fallback)
		if err != nil {
			return nil, err
		}
		maps.Copy(latest, got)
	}
	return latest, nil
}

// fullName returns the package name to look p up by. purl.Parse lowercases
// golang namespaces, but module paths are case-sensitive
// (github.com/BurntSushi/toml), so those are read from the raw purl.
func fullName(p string, parsed *purl.PURL) string {
	if parsed.Type != "golang" {
		return parsed.FullName()
	}
	name, _, _ := strings.Cut(strings.TrimPrefix(p, "pkg:golang/"), "?")
	name, _, _ = strings.Cut(name, "#")
	name, _, _ = strings.Cut(name, "@")
	if unescaped, err := url.PathUnescape(name); err == nil {
		return unescaped
	}
	return name
}

// get fetches reqURL and returns the response if it's a 200, closing it
// otherwise.
func get(ctx context.Context, c *http.Client, reqURL, accept string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, reqURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Accept", accept)
	resp, err := c.Do(req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		return nil, fmt.Errorf("fetching %s: unexpected status %d", reqURL, resp.StatusCode)
	}
	return resp, nil
}

func getJSON(ctx context.Context, c *http.Client, reqURL string, v any) error {
	resp, err := get(ctx, c, reqURL, "application/json")
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return json.NewDecoder(resp.Body).Decode(v)
}

// npmLatest reads the "latest" dist-tag, which is what npm install resolves
// to. The dist-tags endpoint is a few bytes, unlike the full packument.
// e.g. https://registry.npmjs.org/-/package/@vitejs%2Fplugin-react/dist-tags
func npmLatest(ctx context.Context, c *http.Client, baseURL, name string) (string, error) {
	var tags map[string]string
	// A scoped name's "/" must be encoded: @scope%2Fpkg.
	err := getJSON(ctx, c, baseURL+"/-/package/"+strings.Replace(name, "/", "%2F", 1)+"/dist-tags", &tags)
	return tags["latest"], err
}

// pypiLatest reads info.version, PyPI's own latest stable release (post-
// releases count; pre-releases don't).
// e.g. https://pypi.org/pypi/requests/json
func pypiLatest(ctx context.Context, c *http.Client, baseURL, name string) (string, error) {
	var doc struct {
		Info struct {
			Version string `json:"version"`
		} `json:"info"`
	}
	err := getJSON(ctx, c, baseURL+"/pypi/"+url.PathEscape(name)+"/json", &doc)
	return doc.Info.Version, err
}

// cargoLatest reads max_stable_version, the highest non-pre-release,
// non-yanked version.
// e.g. https://crates.io/api/v1/crates/serde
func cargoLatest(ctx context.Context, c *http.Client, baseURL, name string) (string, error) {
	var doc struct {
		Crate struct {
			MaxStableVersion string `json:"max_stable_version"`
		} `json:"crate"`
	}
	err := getJSON(ctx, c, baseURL+"/api/v1/crates/"+url.PathEscape(name), &doc)
	return doc.Crate.MaxStableVersion, err
}

// goLatest reads the module proxy's @latest, which is what `go get
// module@latest` resolves to.
// e.g. https://proxy.golang.org/github.com/!burnt!sushi/toml/@latest
func goLatest(ctx context.Context, c *http.Client, baseURL, name string) (string, error) {
	var doc struct {
		Version string `json:"Version"`
	}
	err := getJSON(ctx, c, baseURL+"/"+escapeModulePath(name)+"/@latest", &doc)
	return doc.Version, err
}

// escapeModulePath applies the module proxy's case encoding: each
// uppercase letter becomes "!" plus its lowercase form.
func escapeModulePath(path string) string {
	var b strings.Builder
	for _, r := range path {
		if 'A' <= r && r <= 'Z' {
			b.WriteByte('!')
			r += 'a' - 'A'
		}
		b.WriteRune(r)
	}
	return b.String()
}

// mavenLatest picks the highest stable version listed in
// maven-metadata.xml. Its <release> element isn't used: it's just the last
// version deployed, which can be a milestone or a backport.
// e.g. https://repo1.maven.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
func mavenLatest(ctx context.Context, c *http.Client, baseURL, name string) (string, error) {
	group, artifact, ok := strings.Cut(name, ":")
	if !ok {
		return "", fmt.Errorf("invalid Maven coordinate %q", name)
	}
	resp, err := get(ctx, c, baseURL+"/"+strings.ReplaceAll(group, ".", "/")+"/"+artifact+"/maven-metadata.xml", "application/xml")
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var doc struct {
		Versions []string `xml:"versioning>versions>version"`
	}
	if err := xml.NewDecoder(resp.Body).Decode(&doc); err != nil {
		return "", err
	}
	var latest string
	for _, v := range doc.Versions {
		// Skips alpha, beta, milestone (M1), rc/cr, and SNAPSHOT versions.
		if !vers.IsStableWithScheme(v, "maven") {
			continue
		}
		if latest == "" || vers.CompareWithScheme(v, latest, "maven") > 0 {
			latest = v
		}
	}
	return latest, nil
}
