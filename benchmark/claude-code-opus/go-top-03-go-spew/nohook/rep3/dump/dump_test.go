package dump

import (
	"strings"
	"testing"
)

type node struct {
	Name     string
	Tags     map[string]int
	Children []*node
	Parent   *node
	secret   bool
}

func TestSdumpNestedAndCyclic(t *testing.T) {
	root := &node{Name: "root", Tags: map[string]int{"b": 2, "a": 1}}
	child := &node{Name: "child", Parent: root, secret: true}
	root.Children = append(root.Children, child)

	out := Sdump(root)
	for _, want := range []string{`"root"`, `"child"`, "already shown", "secret: (bool) true"} {
		if !strings.Contains(out, want) {
			t.Errorf("output missing %q:\n%s", want, out)
		}
	}
	if strings.Index(out, `"a"`) > strings.Index(out, `"b"`) {
		t.Errorf("map keys not sorted:\n%s", out)
	}
}
