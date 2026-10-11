package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"syscli/internal/platform"
)

func main() {
	asJSON := flag.Bool("json", false, "print output as JSON")
	flag.Parse()

	info, err := platform.Query()
	if err != nil {
		fmt.Fprintln(os.Stderr, "syscli:", err)
		os.Exit(1)
	}

	if *asJSON {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(info); err != nil {
			fmt.Fprintln(os.Stderr, "syscli:", err)
			os.Exit(1)
		}
		return
	}

	fmt.Printf("OS:      %s\n", info.OS)
	fmt.Printf("Release: %s\n", info.Release)
	fmt.Printf("Machine: %s\n", info.Machine)
	if info.Extra != "" {
		fmt.Printf("Extra:   %s\n", info.Extra)
	}
}
