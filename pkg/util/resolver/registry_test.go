package resolver

import (
	"context"
	"maps"
	"net/http"
	"net/http/httptest"
	"slices"
	"testing"
)

type fallbackStub struct {
	got []string
}

func (f *fallbackStub) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	f.got = append(f.got, purls...)
	latest := make(map[string]string, len(purls))
	for _, p := range purls {
		latest[p] = "v1.0.0"
	}
	return latest, nil
}

func TestRegistryResolverLatestVersions(t *testing.T) {
	responses := map[string]string{
		"/npm/-/package/@vitejs%2Fplugin-react/dist-tags": `{"beta":"7.0.0-beta.1","latest":"6.1.1"}`,
		"/pypi/pypi/python-dateutil/json":                 `{"info":{"version":"2.9.0.post0"}}`,
		"/cargo/api/v1/crates/libc":                       `{"crate":{"max_version":"1.0.0-alpha.4","max_stable_version":"0.2.189"}}`,
		"/golang/github.com/!burnt!sushi/toml/@latest":    `{"Version":"v1.6.0"}`,
		"/maven/org/springframework/boot/spring-boot-starter-web/maven-metadata.xml": `<metadata><versioning>
			<release>4.2.0-M2</release>
			<versions><version>3.5.9</version><version>4.1.1</version><version>4.2.0-M2</version><version>4.0.12</version></versions>
		</versioning></metadata>`,
	}
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, ok := responses[r.URL.EscapedPath()]
		if !ok {
			http.NotFound(w, r)
			return
		}
		w.Write([]byte(body))
	}))
	defer srv.Close()

	fallback := &fallbackStub{}
	r := &RegistryResolver{Fallback: fallback, baseURLs: map[string]string{}}
	for typ := range registries {
		r.baseURLs[typ] = srv.URL + "/" + typ
	}

	got, err := r.LatestVersions(context.Background(), []string{
		"pkg:npm/%40vitejs/plugin-react",
		"pkg:pypi/python-dateutil",
		"pkg:cargo/libc",
		"pkg:golang/github.com/BurntSushi/toml",
		"pkg:maven/org.springframework.boot/spring-boot-starter-web",
		"pkg:npm/unknown-package",
		"pkg:githubactions/actions/checkout",
	})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}

	want := map[string]string{
		"pkg:npm/%40vitejs/plugin-react":                             "6.1.1",
		"pkg:pypi/python-dateutil":                                   "2.9.0.post0",
		"pkg:cargo/libc":                                             "0.2.189",
		"pkg:golang/github.com/BurntSushi/toml":                      "v1.6.0",
		"pkg:maven/org.springframework.boot/spring-boot-starter-web": "4.1.1",
		"pkg:npm/unknown-package":                                    "v1.0.0",
		"pkg:githubactions/actions/checkout":                         "v1.0.0",
	}
	if !maps.Equal(got, want) {
		t.Errorf("LatestVersions() = %v, want %v", got, want)
	}
	slices.Sort(fallback.got)
	if want := []string{"pkg:githubactions/actions/checkout", "pkg:npm/unknown-package"}; !slices.Equal(fallback.got, want) {
		t.Errorf("fallback got %v, want %v", fallback.got, want)
	}
}
