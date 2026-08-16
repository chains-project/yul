package maven

import (
	"context"
	"testing"
)

type fakeResolver struct {
	latest  map[string]string
	lookups int
}

func (r *fakeResolver) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	r.lookups++
	result := make(map[string]string, len(purls))
	for _, purl := range purls {
		if version, ok := r.latest[purl]; ok {
			result[purl] = version
		}
	}
	return result, nil
}

func TestParsePOMPinsCollectsSupportedDeclarations(t *testing.T) {
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
		<dependency>
			<groupId>org.example</groupId>
			<artifactId>property</artifactId>
			<version>${property.version}</version>
		</dependency>
	</dependencies>
	<dependencyManagement>
		<dependencies>
			<dependency>
				<groupId>org.example</groupId>
				<artifactId>managed</artifactId>
				<version>3.0.0</version>
			</dependency>
			<dependency>
				<groupId>org.example</groupId>
				<artifactId>range</artifactId>
				<version>[3.0.0,4.0.0)</version>
			</dependency>
			<dependency>
				<groupId>org.example</groupId>
				<artifactId>exact-range</artifactId>
				<version>[3.1.0]</version>
			</dependency>
		</dependencies>
	</dependencyManagement>
	<build>
		<plugins>
			<plugin>
				<artifactId>maven-compiler-plugin</artifactId>
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
			<id>release</id>
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

	got, err := parsePOMPins(content)
	if err != nil {
		t.Fatalf("parsePOMPins() error = %v", err)
	}

	want := map[string]string{
		"parent/org.example:parent":                                                                                 "1.0.0",
		"dependencies/org.example:runtime":                                                                          "2.0.0",
		"dependencyManagement/dependencies/org.example:managed":                                                     "3.0.0",
		"dependencyManagement/dependencies/org.example:exact-range":                                                 "3.1.0",
		"build/plugins/org.apache.maven.plugins:maven-compiler-plugin":                                              "4.0.0",
		"build/plugins/org.apache.maven.plugins:maven-compiler-plugin/dependencies/org.example:plugin-runtime":      "5.0.0",
		"build/pluginManagement/plugins/org.example:managed-plugin":                                                 "6.0.0",
		"build/extensions/org.example:extension":                                                                    "7.0.0",
		"profiles/release/dependencies/org.example:profile-runtime":                                                 "8.0.0",
		"profiles/release/dependencyManagement/dependencies/org.example:profile-managed":                            "9.0.0",
		"profiles/release/build/plugins/org.example:profile-plugin":                                                 "10.0.0",
		"profiles/release/build/plugins/org.example:profile-plugin/dependencies/org.example:profile-plugin-runtime": "10.1.0",
		"profiles/release/build/pluginManagement/plugins/org.example:profile-managed-plugin":                        "10.2.0",
		"profiles/release/build/extensions/org.example:profile-extension":                                           "11.0.0",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePOMPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, version := range want {
		pin, ok := got[location]
		if !ok {
			t.Errorf("parsePOMPins() missing %q", location)
			continue
		}
		if pin.Version != version {
			t.Errorf("parsePOMPins()[%q].Version = %q, want %q", location, pin.Version, version)
		}
		if pin.PURL == "" {
			t.Errorf("parsePOMPins()[%q].PURL is empty", location)
		}
	}
}

func TestParsePOMPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePOMPins(" \n")
	if err != nil {
		t.Fatalf("parsePOMPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePOMPins(empty) = %#v, want no pins", got)
	}

	if _, err := parsePOMPins("<project>"); err == nil {
		t.Fatal("parsePOMPins(invalid) returned nil error")
	}
}

func TestCheckPOMOnlyChecksChangedPinnedCoordinates(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:maven/org.example/added": "2.0.0"}}

	before := `<project><dependencies>
		<dependency><groupId>org.example</groupId><artifactId>existing</artifactId><version>1.0.0</version></dependency>
	</dependencies></project>`
	after := `<project><dependencies>
		<dependency><groupId>org.example</groupId><artifactId>existing</artifactId><version>1.0.0</version></dependency>
		<dependency><groupId>org.example</groupId><artifactId>added</artifactId><version>1.0.0</version></dependency>
		<dependency><groupId>org.example</groupId><artifactId>managed</artifactId></dependency>
		<dependency><groupId>org.example</groupId><artifactId>property</artifactId><version>${property.version}</version></dependency>
	</dependencies></project>`

	got, err := CheckPOM(before, after, res)
	if err != nil {
		t.Fatalf("CheckPOM() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckPOM() made %d resolver lookups, want 1", res.lookups)
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
