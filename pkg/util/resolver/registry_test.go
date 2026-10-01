package resolver

import (
	"context"
	"slices"
	"testing"

	"github.com/git-pkgs/vers"
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

// TestRegistryResolverLatestVersions queries the real registries. Latest
// versions move, so each package is only checked for a stable version at
// least as new as one already released. Each was picked because its
// registry also lists something a naive lookup would get wrong: a beta
// dist-tag (npm), a post-release (PyPI), a 1.0.0 alpha (Cargo), an
// uppercase module path (Go), and milestones (Maven).
func TestRegistryResolverLatestVersions(t *testing.T) {
	tests := []struct {
		purl, scheme, atLeast string
	}{
		{"pkg:npm/%40vitejs/plugin-react", "npm", "4.0.0"},
		{"pkg:pypi/python-dateutil", "pypi", "2.9.0.post0"},
		{"pkg:cargo/libc", "cargo", "0.2.150"},
		{"pkg:golang/github.com/BurntSushi/toml", "golang", "v1.3.0"},
		{"pkg:maven/org.springframework.boot/spring-boot-starter-web", "maven", "3.0.0"},
	}

	fallback := &fallbackStub{}
	r := &RegistryResolver{Fallback: fallback}

	purls := []string{
		"pkg:npm/yul-test-package-that-does-not-exist",
		"pkg:githubactions/actions/checkout",
	}
	for _, test := range tests {
		purls = append(purls, test.purl)
	}
	got, err := r.LatestVersions(context.Background(), purls)
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}

	for _, test := range tests {
		v, ok := got[test.purl]
		if !ok {
			t.Errorf("%s: no latest version", test.purl)
			continue
		}
		if !vers.IsStableWithScheme(v, test.scheme) {
			t.Errorf("%s: latest %q is not a stable version", test.purl, v)
		}
		if vers.CompareWithScheme(v, test.atLeast, test.scheme) < 0 {
			t.Errorf("%s: latest %q is older than %q", test.purl, v, test.atLeast)
		}
	}

	slices.Sort(fallback.got)
	if want := []string{"pkg:githubactions/actions/checkout", "pkg:npm/yul-test-package-that-does-not-exist"}; !slices.Equal(fallback.got, want) {
		t.Errorf("fallback got %v, want %v", fallback.got, want)
	}
}
