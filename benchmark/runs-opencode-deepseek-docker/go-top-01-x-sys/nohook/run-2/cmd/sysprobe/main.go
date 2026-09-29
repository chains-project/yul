package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"runtime"
	"time"

	"example.com/sysprobe/internal/sysinfo"
)

var version = "dev"

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	switch os.Args[1] {
	case "uptime":
		runUptime(os.Args[2:])
	case "version":
		runVersion()
	case "help", "-h", "--help":
		usage()
	default:
		fmt.Fprintf(os.Stderr, "sysprobe: unknown command %q\n\n", os.Args[1])
		usage()
		os.Exit(2)
	}
}

func runUptime(args []string) {
	fs := flag.NewFlagSet("uptime", flag.ExitOnError)
	asJSON := fs.Bool("json", false, "emit output as JSON")
	_ = fs.Parse(args)

	d, err := sysinfo.Uptime()
	if err != nil {
		fmt.Fprintln(os.Stderr, "sysprobe:", err)
		os.Exit(1)
	}

	if *asJSON {
		payload := struct {
			OS            string `json:"os"`
			Arch          string `json:"arch"`
			UptimeSeconds int64  `json:"uptime_seconds"`
			Uptime        string `json:"uptime"`
		}{
			OS:            runtime.GOOS,
			Arch:          runtime.GOARCH,
			UptimeSeconds: int64(d.Seconds()),
			Uptime:        d.Round(time.Second).String(),
		}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(payload); err != nil {
			fmt.Fprintln(os.Stderr, "sysprobe:", err)
			os.Exit(1)
		}
		return
	}

	fmt.Printf("up %s (%s/%s)\n", d.Round(time.Second), runtime.GOOS, runtime.GOARCH)
}

func runVersion() {
	fmt.Printf("sysprobe %s %s/%s\n", version, runtime.GOOS, runtime.GOARCH)
}

func usage() {
	fmt.Fprint(os.Stderr, `usage: sysprobe <command> [flags]

commands:
  uptime     print system uptime
  version    print version information

flags for uptime:
  -json      emit output as JSON
`)
}
