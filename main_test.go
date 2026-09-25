package main

import (
	"context"
	"reflect"
	"testing"

	"github.com/chains-project/yul/pkg/githubactions"
	"github.com/chains-project/yul/pkg/golang"
	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
)

type stubResolver struct{}

func (*stubResolver) LatestVersions(context.Context, []string) (map[string]string, error) {
	return nil, nil
}

func TestCheckerFor(t *testing.T) {
	tests := []struct {
		filename string
		want     any
	}{
		{filename: "pom.xml", want: maven.Checker{}},
		{filename: "requirements.txt", want: pypi.RequirementsChecker{}},
		{filename: "pyproject.toml", want: pypi.PyprojectChecker{}},
		{filename: "package.json", want: npm.Checker{}},
		{filename: ".github/workflows/ci.yml", want: githubactions.Checker{}},
		{filename: "/home/user/project/.github/workflows/release.yaml", want: githubactions.Checker{}},
		{filename: "go.mod", want: golang.Checker{}},
	}

	checkers := newCheckers(nil)
	for _, test := range tests {
		t.Run(test.filename, func(t *testing.T) {
			got := checkerFor(checkers, test.filename)
			if got == nil {
				t.Fatalf("checkerFor(%q) returned nil", test.filename)
			}
			if reflect.TypeOf(got) != reflect.TypeOf(test.want) {
				t.Fatalf("checkerFor(%q) returned %T, want %T", test.filename, got, test.want)
			}
		})
	}
}

func TestCheckerForUnknownManifest(t *testing.T) {
	if got := checkerFor(newCheckers(nil), "Gemfile"); got != nil {
		t.Fatalf("checkerFor(%q) returned %T, want nil", "Gemfile", got)
	}
}

func TestNewCheckersWiresResolverIntoMaven(t *testing.T) {
	res := &stubResolver{}
	checker, ok := checkerFor(newCheckers(res), "pom.xml").(maven.Checker)
	if !ok {
		t.Fatal("pom.xml checker is not maven.Checker")
	}
	if checker.Resolver != res {
		t.Fatal("maven.Checker does not use the shared resolver")
	}
}

func TestLooksLikeManifestWrite(t *testing.T) {
	tests := []struct {
		name string
		cmd  string
		want bool
	}{
		{"redirect to requirements.txt", `cat > requirements.txt << 'EOF'`, true},
		{"append redirect", `echo "foo==1.0" >> requirements.txt`, true},
		{"tee", `echo pinned >> pom.xml; tee pom.xml`, true},
		{"sed -i", `sed -i 's/1.0/2.0/' package.json`, true},
		{"perl -i", `perl -i -pe 's/1.0/2.0/' Cargo.toml`, true},
		{"dd of=", `dd of=go.mod if=/tmp/x`, true},
		{"cp onto manifest", `cp /tmp/pom.xml pom.xml`, true},
		{"mv onto manifest", `mv /tmp/new.mod go.mod`, true},
		{"github actions workflow redirect", `cat > .github/workflows/ci.yml << 'EOF'`, true},
		{"quoted path redirect", `printf '%s' "$content" > "requirements.txt"`, true},

		{"plain read", `cat requirements.txt`, false},
		{"grep manifest", `grep react package.json`, false},
		{"git diff manifest", `git diff pom.xml`, false},
		{"pip install using requirements", `pip install -r requirements.txt`, false},
		{"fd duplication near manifest name, not a file write", `mvn test 2>&1 | grep -i pom.xml`, false},
		{"unrelated file redirect", `echo hi > notes.txt`, false},
		{"mkdir unrelated", `mkdir -p .github/workflows`, false},
		{"ls workflows dir", `ls -la .github/workflows/`, false},

		// Regression cases: stderr-to-file (not fd dup) or an unrelated `>`
		// elsewhere in the command used to false-positive because the old
		// check only required the manifest name and *some* `>` to co-occur
		// anywhere in cmd, rather than requiring the `>` to actually target
		// the manifest.
		{"read with stderr to /dev/null", `cat Cargo.toml 2>/dev/null`, false},
		{"read with stderr to /dev/null, compound", `ls -la && cat go.mod 2>/dev/null; go version`, false},
		{"unrelated redirect elsewhere, manifest read in same clause", `npm init -y >/dev/null && cat package.json`, false},
		{"manifest named in different clause than the write", `cat > .gitignore << 'EOF'
ignored
EOF
git add pyproject.toml .gitignore`, false},
		{"manifest mentioned in a URL, no local write", `curl -s "https://example.com/spring-boot/pom.xml" | grep version`, false},
		{"manifest mentioned inside a string literal, unrelated redirect", `python3 -c "print('pyproject.toml')" > /tmp/out.log`, false},
		{"find pattern for manifest name, not a write", `find . -iname "go.mod" 2>/dev/null`, false},

		{"redirect target is the manifest despite trailing stderr redirect", `cat > pom.xml << 'EOF'
<project/>
EOF
` + "true", true},
		{"sed -i with trailing pipe to unrelated command", `sed -i 's/1.0/2.0/' package.json | cat`, true},
		{"append redirect with terminator", `echo pinned >> Cargo.toml; echo done`, true},
		{"heredoc write to manifest in a scratch dir", `cd /tmp/x && cat > go.mod <<'EOF'
module tmp
EOF`, true},
		{"mv with multiple sources including the manifest", `mv a.txt pom.xml src .`, true},
		{"redirect target with a relative directory prefix", `cat > node_modules/pkg-a/package.json <<'EOF'
{}
EOF`, true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := looksLikeManifestWrite(test.cmd); got != test.want {
				t.Errorf("looksLikeManifestWrite(%q) = %v, want %v", test.cmd, got, test.want)
			}
		})
	}
}
