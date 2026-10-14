package inspect

import (
	"strings"
	"testing"
)

type node struct {
	Name     string
	children []*node
	parent   *node
	meta     map[string]int
}

func TestSdumpDeepAndCyclic(t *testing.T) {
	root := &node{Name: "root", meta: map[string]int{"b": 2, "a": 1}}
	child := &node{Name: "child", parent: root}
	root.children = append(root.children, child)

	out := Sdump(root)

	for _, want := range []string{"root", "child", "children", "already shown"} {
		if !strings.Contains(out, want) {
			t.Errorf("output missing %q:\n%s", want, out)
		}
	}
	if strings.Index(out, `"a"`) > strings.Index(out, `"b"`) {
		t.Errorf("map keys not sorted:\n%s", out)
	}
	if Sdump(root) != out {
		t.Error("output is not deterministic")
	}
}
