// Command sysprobe prints system information gathered through low-level
// kernel interfaces that the Go standard library does not expose.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"example.com/sysprobe/internal/sysinfo"
)

func main() {
	asJSON := flag.Bool("json", false, "emit machine-readable JSON instead of text")
	flag.Parse()

	info, err := sysinfo.Gather()
	if err != nil {
		fmt.Fprintln(os.Stderr, "sysprobe:", err)
		os.Exit(1)
	}

	if *asJSON {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(info); err != nil {
			fmt.Fprintln(os.Stderr, "sysprobe:", err)
			os.Exit(1)
		}
		return
	}

	fmt.Print(info.Text())
}
