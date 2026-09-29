package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"example.com/syscallkit/internal/native"
)

func main() {
	asJSON := flag.Bool("json", false, "emit output as JSON")
	flag.Parse()

	platform := native.Current()
	up, err := native.Uptime()
	if err != nil {
		fmt.Fprintln(os.Stderr, "syscallkit:", err)
		os.Exit(1)
	}

	if *asJSON {
		out := map[string]any{
			"os":             platform.OS,
			"arch":           platform.Arch,
			"uptime_seconds": int64(up.Seconds()),
		}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(out); err != nil {
			fmt.Fprintln(os.Stderr, "syscallkit:", err)
			os.Exit(1)
		}
		return
	}

	fmt.Printf("os:     %s\n", platform.OS)
	fmt.Printf("arch:   %s\n", platform.Arch)
	fmt.Printf("uptime: %s\n", up)
}
