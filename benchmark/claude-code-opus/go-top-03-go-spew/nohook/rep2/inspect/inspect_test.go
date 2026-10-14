package inspect

import (
	"strings"
	"testing"
)

type node struct {
	Name     string
	secret   int
	Children []*node
	Parent   *node
	Meta     map[string]any
}

func TestSdumpNestedAndCyclic(t *testing.T) {
	root := &node{Name: "root", secret: 42, Meta: map[string]any{"b": 2, "a": []int{1}}}
	child := &node{Name: "child", Parent: root}
	root.Children = append(root.Children, child)

	out := Sdump(root)
	for _, want := range []string{`"root"`, `"child"`, "secret: (int) 42", "already shown"} {
		if !strings.Contains(out, want) {
			t.Errorf("output missing %q:\n%s", want, out)
		}
	}
	if strings.Index(out, `"a"`) > strings.Index(out, `"b"`) {
		t.Errorf("map keys not sorted:\n%s", out)
	}
}
