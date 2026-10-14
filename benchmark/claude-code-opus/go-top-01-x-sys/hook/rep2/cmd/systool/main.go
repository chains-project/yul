// Command systool is a CLI that uses low-level OS interfaces via golang.org/x/sys.
package main

import (
	"fmt"
	"os"

	"example.com/systool/internal/sys"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "systool:", err)
		os.Exit(1)
	}
}

func run() error {
	cols, rows, err := sys.TerminalSize(os.Stdout)
	if err != nil {
		return fmt.Errorf("terminal size: %w", err)
	}
	fmt.Printf("terminal: %dx%d\n", cols, rows)
	return nil
}
