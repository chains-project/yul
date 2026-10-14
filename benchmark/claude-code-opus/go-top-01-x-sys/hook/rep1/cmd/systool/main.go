// Command systool is a cross-platform CLI that uses OS-level system calls
// not exposed by the Go standard library.
package main

import (
	"fmt"
	"os"

	"github.com/example/systool/internal/sysinfo"
)

func main() {
	info, err := sysinfo.Get()
	if err != nil {
		fmt.Fprintf(os.Stderr, "systool: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("os:      %s\n", info.OS)
	fmt.Printf("release: %s\n", info.Release)
	fmt.Printf("arch:    %s\n", info.Machine)
}
