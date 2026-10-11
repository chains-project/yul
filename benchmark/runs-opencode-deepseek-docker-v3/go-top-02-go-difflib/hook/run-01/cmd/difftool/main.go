// Command difftool prints the unified diff between two files.
//
// It exits 0 when the files are identical, 1 when they differ, and 2 on error,
// which makes it convenient to use from tests and scripts.
package main

import (
	"fmt"
	"os"

	"difftool"
)

func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "usage: %s FILE1 FILE2\n", os.Args[0])
		os.Exit(2)
	}

	paths := os.Args[1:]
	contents := make([]string, 2)
	for i, path := range paths {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "%s: %v\n", os.Args[0], err)
			os.Exit(2)
		}
		contents[i] = string(data)
	}

	diff := difftool.UnifiedText(contents[0], contents[1], difftool.Options{
		FromName: paths[0],
		ToName:   paths[1],
	})
	if diff == "" {
		return
	}
	fmt.Print(diff)
	os.Exit(1)
}
