package maven

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// metadataServer stands in for Maven Central. For each coordinate in
// versionsByCoord it serves a maven-metadata.xml carrying that version
// list; every other path 404s. It records the paths it was asked for.
func metadataServer(t *testing.T, versionsByCoord map[string][]string) (*httptest.Server, *[]string) {
	t.Helper()
	toPath := strings.NewReplacer(".", "/", ":", "/")
	bodies := make(map[string]string, len(versionsByCoord))
	for coord, versions := range versionsByCoord {
		var b strings.Builder
		b.WriteString("<metadata><versioning><versions>")
		for _, v := range versions {
			fmt.Fprintf(&b, "<version>%s</version>", v)
		}
		b.WriteString("</versions></versioning></metadata>")
		bodies["/"+toPath.Replace(coord)+"/maven-metadata.xml"] = b.String()
	}

	var asked []string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		asked = append(asked, r.URL.Path)
		if body, ok := bodies[r.URL.Path]; ok {
			_, _ = w.Write([]byte(body))
			return
		}
		http.NotFound(w, r)
	}))
	t.Cleanup(srv.Close)
	return srv, &asked
}

func TestMavenCentralExistenceRealCoordinateAndVersion(t *testing.T) {
	srv, asked := metadataServer(t, map[string][]string{
		"com.google.guava:guava": {"32.1.3-jre", "33.0.0-jre", "33.7.1-jre"},
	})
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	ex, err := c.Existence(context.Background(), "com.google.guava", "guava", "33.0.0-jre")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || !ex.Version {
		t.Fatalf("Existence() = %+v, want Package and Version both true", ex)
	}
	if got := (*asked)[0]; got != "/com/google/guava/guava/maven-metadata.xml" {
		t.Fatalf("requested %q, want the group-as-path metadata URL", got)
	}
}

func TestMavenCentralExistenceUnknownVersion(t *testing.T) {
	srv, _ := metadataServer(t, map[string][]string{
		"com.google.guava:guava": {"32.1.3-jre", "33.0.0-jre"},
	})
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	ex, err := c.Existence(context.Background(), "com.google.guava", "guava", "99.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || ex.Version {
		t.Fatalf("Existence() = %+v, want Package true, Version false", ex)
	}
}

func TestMavenCentralExistenceNoVersionQueried(t *testing.T) {
	srv, _ := metadataServer(t, map[string][]string{
		"com.google.guava:guava": {"33.0.0-jre"},
	})
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	ex, err := c.Existence(context.Background(), "com.google.guava", "guava", "")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package {
		t.Fatalf("Existence() = %+v, want Package true", ex)
	}
}

func TestMavenCentralExistenceMissingCoordinate(t *testing.T) {
	srv, _ := metadataServer(t, map[string][]string{
		"com.google.guava:guava": {"33.0.0-jre"},
	})
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	ex, err := c.Existence(context.Background(), "com.example", "invented-lib", "1.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v, want nil for a 404", err)
	}
	if ex.Package {
		t.Fatalf("Existence() = %+v, want Package false for a 404 coordinate", ex)
	}
}

func TestMavenCentralExistenceEmptyVersionListDoesNotFlag(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("<metadata><versioning><versions></versions></versioning></metadata>"))
	}))
	t.Cleanup(srv.Close)
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	ex, err := c.Existence(context.Background(), "com.example", "weird", "1.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || !ex.Version {
		t.Fatalf("Existence() = %+v, want both true (empty list is not proof the version is missing)", ex)
	}
}

func TestMavenCentralExistenceInconclusiveOnServerError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		http.Error(w, "boom", http.StatusInternalServerError)
	}))
	t.Cleanup(srv.Close)
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	if _, err := c.Existence(context.Background(), "com.example", "lib", "1.0.0"); err == nil {
		t.Fatal("Existence() error = nil, want an error for a 500 (so the caller fails open)")
	}
}

func TestMavenCentralExistenceInconclusiveOnTransportError(t *testing.T) {
	c := &MavenCentralExistenceChecker{BaseURL: "http://127.0.0.1:1"} // nothing listening

	if _, err := c.Existence(context.Background(), "com.example", "lib", "1.0.0"); err == nil {
		t.Fatal("Existence() error = nil, want a transport error")
	}
}

func TestMavenCentralExistenceInconclusiveOnBadXML(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("<metadata><versioning><versions"))
	}))
	t.Cleanup(srv.Close)
	c := &MavenCentralExistenceChecker{BaseURL: srv.URL}

	if _, err := c.Existence(context.Background(), "com.example", "lib", "1.0.0"); err == nil {
		t.Fatal("Existence() error = nil, want an error for unparseable metadata")
	}
}
