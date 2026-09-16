package main

import (
	"flag"
	"fmt"
	"os"

	"hook/internal/sys"
)

func main() {
	flag.Parse()
	cmd := flag.Arg(0)

	switch cmd {
	case "info":
		info, err := sys.GetInfo()
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Platform: %s\n", info.Platform)
		fmt.Printf("OS: %s\n", info.OS)
		fmt.Printf("Arch: %s\n", info.Arch)
	default:
		fmt.Println("hook - low-level system call CLI")
		fmt.Println()
		fmt.Println("Usage:")
		fmt.Println("  hook info    Show system information")
	}
}