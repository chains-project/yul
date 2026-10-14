// Command systool reports low-level OS information via native system calls.
package main

import (
	"fmt"
	"os"
	"runtime"

	"example.com/systool/internal/platform"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "systool:", err)
		os.Exit(1)
	}
}

func run() error {
	info, err := platform.GetInfo()
	if err != nil {
		return fmt.Errorf("get os info: %w", err)
	}
	uptime, err := platform.Uptime()
	if err != nil {
		return fmt.Errorf("get uptime: %w", err)
	}

	fmt.Printf("platform: %s/%s\n", runtime.GOOS, runtime.GOARCH)
	fmt.Printf("kernel:   %s %s\n", info.Name, info.Release)
	fmt.Printf("version:  %s\n", info.Version)
	fmt.Printf("uptime:   %s\n", uptime)

	if cols, rows, err := platform.TermSize(os.Stdout); err == nil {
		fmt.Printf("terminal: %dx%d\n", cols, rows)
	} else {
		fmt.Printf("terminal: n/a (%v)\n", err)
	}
	return nil
}
