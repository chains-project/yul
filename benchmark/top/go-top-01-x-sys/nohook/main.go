// Command syscli reports free disk space for a path using low-level
// syscalls not exposed by the standard library.
package main

import (
	"fmt"
	"os"
)

func main() {
	path := "."
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	free, total, err := diskFree(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "syscli: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("%s: %d / %d bytes free\n", path, free, total)
}
