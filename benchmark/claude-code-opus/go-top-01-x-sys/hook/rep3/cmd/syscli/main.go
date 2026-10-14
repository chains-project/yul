// Command syscli is a CLI tool that uses OS-level system calls not exposed
// by the Go standard library.
package main

import (
	"fmt"
	"os"

	"github.com/example/syscli/internal/platform"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "syscli:", err)
		os.Exit(1)
	}
}

func run() error {
	release, err := platform.KernelRelease()
	if err != nil {
		return fmt.Errorf("kernel release: %w", err)
	}
	fmt.Println("kernel:", release)

	cols, rows, err := platform.TerminalSize(os.Stdout)
	if err != nil {
		fmt.Println("terminal: not a terminal")
	} else {
		fmt.Printf("terminal: %dx%d\n", cols, rows)
	}
	return nil
}
