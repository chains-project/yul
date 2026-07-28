package maven

import (
	"io"
	"net/http"
	"strings"
	"testing"
)

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req)
}

func TestParsePOMCollectsSupportedCoordinates(t *testing.T) {
	content := `<project>
	<parent>
		<groupId>org.example</groupId>
		<artifactId>parent</artifactId>
		<version>1.0.0</version>
	</parent>
	<dependencies>
		<dependency>
			<groupId>org.example</groupId>
			<artifactId>runtime</artifactId>
			<version>2.0.0</version>
		</dependency>
		<dependency>
			<groupId>org.example</groupId>
			<artifactId>managed</artifactId>
		</dependency>
	</dependencies>
	<dependencyManagement>
		<dependencies>
			<dependency>
				<groupId>org.example</groupId>
				<artifactId>managed</artifactId>
				<version>3.0.0</version>
			</dependency>
		</dependencies>
	</dependencyManagement>
	<build>
		<plugins>
			<plugin>
				<groupId>org.example</groupId>
				<artifactId>plugin</artifactId>
				<version>4.0.0</version>
				<dependencies>
					<dependency>
						<groupId>org.example</groupId>
						<artifactId>plugin-runtime</artifactId>
						<version>5.0.0</version>
					</dependency>
				</dependencies>
			</plugin>
		</plugins>
		<pluginManagement>
			<plugins>
				<plugin>
					<groupId>org.example</groupId>
					<artifactId>managed-plugin</artifactId>
					<version>6.0.0</version>
				</plugin>
			</plugins>
		</pluginManagement>
		<extensions>
			<extension>
				<groupId>org.example</groupId>
				<artifactId>extension</artifactId>
				<version>7.0.0</version>
			</extension>
		</extensions>
	</build>
	<profiles>
		<profile>
			<dependencies>
				<dependency>
					<groupId>org.example</groupId>
					<artifactId>profile-runtime</artifactId>
					<version>8.0.0</version>
				</dependency>
			</dependencies>
			<dependencyManagement>
				<dependencies>
					<dependency>
						<groupId>org.example</groupId>
						<artifactId>profile-managed</artifactId>
						<version>9.0.0</version>
					</dependency>
				</dependencies>
			</dependencyManagement>
			<build>
				<plugins>
					<plugin>
						<groupId>org.example</groupId>
						<artifactId>profile-plugin</artifactId>
						<version>10.0.0</version>
						<dependencies>
							<dependency>
								<groupId>org.example</groupId>
								<artifactId>profile-plugin-runtime</artifactId>
								<version>10.1.0</version>
							</dependency>
						</dependencies>
					</plugin>
				</plugins>
				<pluginManagement>
					<plugins>
						<plugin>
							<groupId>org.example</groupId>
							<artifactId>profile-managed-plugin</artifactId>
							<version>10.2.0</version>
						</plugin>
					</plugins>
				</pluginManagement>
				<extensions>
					<extension>
						<groupId>org.example</groupId>
						<artifactId>profile-extension</artifactId>
						<version>11.0.0</version>
					</extension>
				</extensions>
			</build>
		</profile>
	</profiles>
</project>`

	got, err := parsePOM(content)
	if err != nil {
		t.Fatalf("parsePOM() error = %v", err)
	}

	want := map[string]string{
		"parent:org.example:parent":                                       "1.0.0",
		"dependency:org.example:runtime":                                  "2.0.0",
		"dependency:org.example:managed":                                  "",
		"managed-dependency:org.example:managed":                          "3.0.0",
		"plugin:org.example:plugin":                                       "4.0.0",
		"plugin-dependency:org.example:plugin-runtime":                    "5.0.0",
		"managed-plugin:org.example:managed-plugin":                       "6.0.0",
		"extension:org.example:extension":                                 "7.0.0",
		"profile[0]-dependency:org.example:profile-runtime":               "8.0.0",
		"profile[0]-managed-dependency:org.example:profile-managed":       "9.0.0",
		"profile[0]-plugin:org.example:profile-plugin":                    "10.0.0",
		"profile[0]-plugin-dependency:org.example:profile-plugin-runtime": "10.1.0",
		"profile[0]-managed-plugin:org.example:profile-managed-plugin":    "10.2.0",
		"profile[0]-extension:org.example:profile-extension":              "11.0.0",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePOM() returned %d coordinates, want %d: %#v", len(got), len(want), got)
	}
	for key, version := range want {
		entry, ok := got[key]
		if !ok {
			t.Errorf("parsePOM() missing %q", key)
			continue
		}
		if entry.Version != version {
			t.Errorf("parsePOM()[%q].Version = %q, want %q", key, entry.Version, version)
		}
	}
}

func TestParsePOMEmptyAndInvalid(t *testing.T) {
	got, err := parsePOM(" \n")
	if err != nil {
		t.Fatalf("parsePOM(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePOM(empty) = %#v, want no coordinates", got)
	}

	if _, err := parsePOM("<project>"); err == nil {
		t.Fatal("parsePOM(invalid) returned nil error")
	}
}

func TestCheckPOMOnlyChecksChangedPinnedCoordinates(t *testing.T) {
	originalTransport := http.DefaultTransport
	requests := 0
	http.DefaultTransport = roundTripFunc(func(req *http.Request) (*http.Response, error) {
		requests++
		if req.URL.String() != "https://repo1.maven.org/maven2/org/example/added/maven-metadata.xml" {
			t.Fatalf("unexpected registry request: %s", req.URL)
		}
		return &http.Response{
			StatusCode: http.StatusOK,
			Status:     "200 OK",
			Body: io.NopCloser(strings.NewReader(
				`<metadata><versioning><latest>3.0.0</latest><release>2.0.0</release></versioning></metadata>`,
			)),
			Header: make(http.Header),
		}, nil
	})
	t.Cleanup(func() {
		http.DefaultTransport = originalTransport
	})

	before := `<project><dependencies>
		<dependency><groupId>org.example</groupId><artifactId>existing</artifactId><version>1.0.0</version></dependency>
	</dependencies></project>`
	after := `<project><dependencies>
		<dependency><groupId>org.example</groupId><artifactId>existing</artifactId><version>1.0.0</version></dependency>
		<dependency><groupId>org.example</groupId><artifactId>added</artifactId><version>1.0.0</version></dependency>
		<dependency><groupId>org.example</groupId><artifactId>managed</artifactId></dependency>
	</dependencies></project>`

	got, err := CheckPOM(before, after)
	if err != nil {
		t.Fatalf("CheckPOM() error = %v", err)
	}
	if requests != 1 {
		t.Fatalf("CheckPOM() made %d registry requests, want 1", requests)
	}
	if len(got) != 1 {
		t.Fatalf("CheckPOM() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Namespace != "org.example" ||
		got[0].Name != "added" ||
		got[0].Current != "1.0.0" ||
		got[0].Latest != "2.0.0" {
		t.Fatalf("CheckPOM() mismatch = %#v", got[0])
	}
}
