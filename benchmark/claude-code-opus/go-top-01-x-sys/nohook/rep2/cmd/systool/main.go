package main

import (
	"fmt"
	"os"

	"example.com/systool/internal/platform"
)

func main() {
	info, err := platform.Query()
	if err != nil {
		fmt.Fprintln(os.Stderr, "systool:", err)
		os.Exit(1)
	}
	fmt.Printf("os:      %s\n", info.OS)
	fmt.Printf("release: %s\n", info.Release)
	fmt.Printf("machine: %s\n", info.Machine)
	fmt.Printf("memory:  %d MiB\n", info.TotalMemory>>20)
}
