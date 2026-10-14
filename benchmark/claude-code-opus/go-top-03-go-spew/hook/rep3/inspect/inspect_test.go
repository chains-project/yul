package inspect

import (
	"strings"
	"testing"
)

type node struct {
	Name     string
	Children []*node
	Meta     map[string]int
	parent   *node
}

func TestSdumpNestedAndCyclic(t *testing.T) {
	root := &node{Name: "root", Meta: map[string]int{"b": 2, "a": 1}}
	child := &node{Name: "child", parent: root}
	root.Children = append(root.Children, child)

	out := Sdump(root)
	for _, want := range []string{`"root"`, `"child"`, "parent:", "already shown"} {
		if !strings.Contains(out, want) {
			t.Errorf("output missing %q:\n%s", want, out)
		}
	}
	if strings.Index(out, `"a"`) > strings.Index(out, `"b"`) {
		t.Errorf("map keys not sorted:\n%s", out)
	}
}
