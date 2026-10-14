// Command debugdump demonstrates the dump package on a sample structure.
package main

import (
	"os"

	"debugdump/dump"
)

type item struct {
	ID    int
	Attrs map[string]any
	Next  *item
}

func main() {
	a := &item{ID: 1, Attrs: map[string]any{"color": "red", "sizes": []int{1, 2, 3}}}
	b := &item{ID: 2, Next: a}
	a.Next = b // cycle
	dump.Fdump(os.Stdout, a)
}
