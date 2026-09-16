package main

import (
	"fmt"
	"os"

	"syscli/platform"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: syscli <command>")
		fmt.Println("")
		fmt.Println("Available commands:")
		fmt.Println("  info    Show system and platform information")
		fmt.Println("  getpid  Print the current process ID")
		os.Exit(0)
	}

	switch os.Args[1] {
	case "info":
		info, err := platform.SysInfo()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Println(info)

	case "getpid":
		pid, err := platform.GetPID()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Println(pid)

	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", os.Args[1])
		os.Exit(1)
	}
}