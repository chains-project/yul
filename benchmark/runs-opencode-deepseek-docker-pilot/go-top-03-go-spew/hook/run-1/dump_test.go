package debugprint

import (
	"strings"
	"testing"
)

type sampleInner struct {
	Exported   string
	unexported int
}

type sample struct {
	Name string
	In   sampleInner
	Tags []string
	Meta map[string]int
}

type node struct {
	Label string
	Next  *node
}

type customStringer struct{ V int }

func (c customStringer) String() string { return "custom" }

type customError struct{}

func (customError) Error() string { return "boom" }

func sdump(t *testing.T, cfg Config, a ...any) string {
	t.Helper()
	var b strings.Builder
	if err := fdump(&b, cfg, a...); err != nil {
		t.Fatalf("fdump returned error: %v", err)
	}
	return b.String()
}

func TestBasicKinds(t *testing.T) {
	cfg := DefaultConfig
	cfg.DisablePointerAddresses = true
	cases := []struct {
		val  any
		want string
	}{
		{42, "(int) 42\n"},
		{"hi", "(string) (len=2) \"hi\"\n"},
		{true, "(bool) true\n"},
		{3.5, "(float64) 3.5\n"},
		{complex(1, 2), "(complex128) (1+2i)\n"},
		{nil, "<nil>\n"},
		{(*int)(nil), "(*int) nil\n"},
	}
	for _, tc := range cases {
		if got := sdump(t, cfg, tc.val); got != tc.want {
			t.Errorf("Sdump(%#v) = %q, want %q", tc.val, got, tc.want)
		}
	}
}

func TestStructDeepPrintUnexported(t *testing.T) {
	cfg := Config{Indent: "  ", DisablePointerAddresses: true, SortKeys: true}
	v := sample{
		Name: "x",
		In:   sampleInner{Exported: "e", unexported: 7},
		Tags: []string{"a", "b"},
		Meta: map[string]int{"b": 2, "a": 1},
	}
	want := `(debugprint.sample){
  Name: (string) (len=1) "x"
  In: (debugprint.sampleInner){
    Exported: (string) (len=1) "e"
    unexported: (int) 7
  }
  Tags: ([]string)[2/2]{
    (string) (len=1) "a"
    (string) (len=1) "b"
  }
  Meta: (map[string]int)(len=2){
    (string) (len=1) "a": (int) 1
    (string) (len=1) "b": (int) 2
  }
}
`
	if got := sdump(t, cfg, v); got != want {
		t.Errorf("unexpected dump:\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestCycleDetection(t *testing.T) {
	cfg := Config{Indent: " ", DisablePointerAddresses: true}
	n := &node{Label: "root"}
	n.Next = n
	got := sdump(t, cfg, n)
	if !strings.Contains(got, "<already shown>") {
		t.Errorf("expected cycle marker, got:\n%s", got)
	}
}

func TestMethods(t *testing.T) {
	if got, want := sdump(t, DefaultConfig, customStringer{V: 5}), "(debugprint.customStringer) \"custom\"\n"; got != want {
		t.Errorf("Stringer = %q, want %q", got, want)
	}
	if got, want := sdump(t, DefaultConfig, customError{}), "(debugprint.customError) \"boom\"\n"; got != want {
		t.Errorf("error = %q, want %q", got, want)
	}
	cfg := Config{Indent: " ", DisableMethods: true}
	if got := sdump(t, cfg, customStringer{V: 5}); strings.Contains(got, "\"custom\"") {
		t.Errorf("DisableMethods should suppress Stringer, got:\n%s", got)
	}
}

func TestMaxDepth(t *testing.T) {
	cfg := Config{Indent: " ", MaxDepth: 1}
	v := sample{Name: "x", In: sampleInner{Exported: "e"}}
	got := sdump(t, cfg, v)
	if !strings.Contains(got, "(debugprint.sampleInner)...") {
		t.Errorf("expected truncated nested value, got:\n%s", got)
	}
}

func TestPointerAddresses(t *testing.T) {
	v := &sample{Name: "x"}
	got := sdump(t, DefaultConfig, v)
	if !strings.Contains(got, "0x") {
		t.Errorf("expected pointer address, got:\n%s", got)
	}
	cfg := DefaultConfig
	cfg.DisablePointerAddresses = true
	if got := sdump(t, cfg, v); strings.Contains(got, "0x") {
		t.Errorf("DisablePointerAddresses should hide addresses, got:\n%s", got)
	}
}

func TestCapacities(t *testing.T) {
	cfg := Config{Indent: " ", DisableCapacities: true}
	if got, want := sdump(t, cfg, []int{1}), "([]int)[1]{\n (int) 1\n}\n"; got != want {
		t.Errorf("slice = %q, want %q", got, want)
	}
}

func TestMultipleArgs(t *testing.T) {
	if got, want := sdump(t, DefaultConfig, 1, 2), "(int) 1\n(int) 2\n"; got != want {
		t.Errorf("multi = %q, want %q", got, want)
	}
}

func TestSdump(t *testing.T) {
	if got, want := Sdump(7), "(int) 7\n"; got != want {
		t.Errorf("Sdump = %q, want %q", got, want)
	}
}
