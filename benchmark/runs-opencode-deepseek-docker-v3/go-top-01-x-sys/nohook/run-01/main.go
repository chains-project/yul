package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"example.com/syscli/internal/sysinfo"
)

var version = "dev"

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "syscli:", err)
		os.Exit(1)
	}
}

func run() error {
	asJSON := flag.Bool("json", false, "encode output as JSON")
	showVersion := flag.Bool("version", false, "print version and exit")
	flag.Parse()

	if *showVersion {
		fmt.Println(version)
		return nil
	}

	info, err := sysinfo.Collect()
	if err != nil {
		return err
	}

	if *asJSON {
		return json.NewEncoder(os.Stdout).Encode(map[string]float64{
			"uptime_seconds": info.Uptime.Seconds(),
		})
	}

	fmt.Println(info.Uptime.Round(time.Second))
	return nil
}
