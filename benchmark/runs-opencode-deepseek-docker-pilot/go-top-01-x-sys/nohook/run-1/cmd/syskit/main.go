// Command syskit is a small CLI that reports host details gathered through
// low-level system calls which the Go standard library does not wrap.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"example.com/syskit/internal/platform"
)

func main() {
	asJSON := flag.Bool("json", false, "emit the result as JSON")
	flag.Parse()

	info, err := platform.Info()
	if err != nil {
		fmt.Fprintf(os.Stderr, "syskit: %v\n", err)
		os.Exit(1)
	}

	if *asJSON {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(info); err != nil {
			fmt.Fprintf(os.Stderr, "syskit: %v\n", err)
			os.Exit(1)
		}
		return
	}

	fmt.Printf("os:      %s\n", info.OS)
	fmt.Printf("release: %s\n", info.Release)
	fmt.Printf("version: %s\n", info.Version)
	fmt.Printf("machine: %s\n", info.Machine)
}
