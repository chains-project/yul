// Command syscli is a small cross-platform CLI that demonstrates accessing
// low-level kernel information through syscalls that are not exposed by the
// Go standard library.
package main

import (
	"fmt"
	"os"

	"github.com/example/syscli/internal/syscallx"
)

func main() {
	version, err := syscallx.KernelVersion()
	if err != nil {
		fmt.Fprintf(os.Stderr, "syscli: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(version)
}
