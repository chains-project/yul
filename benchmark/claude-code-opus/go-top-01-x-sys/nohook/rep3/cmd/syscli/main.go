// Command syscli reports low-level system information using
// platform-specific system calls.
package main

import (
	"fmt"
	"os"

	"github.com/example/syscli/internal/platform"
)

func main() {
	info, err := platform.Info()
	if err != nil {
		fmt.Fprintf(os.Stderr, "syscli: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("os:      %s\n", info.OS)
	fmt.Printf("release: %s\n", info.Release)
	fmt.Printf("arch:    %s\n", info.Arch)
	fmt.Printf("uptime:  %s\n", info.Uptime)
}
