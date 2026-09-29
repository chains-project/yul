package main

import (
	"flag"
	"fmt"
	"os"
	"runtime"
	"time"

	"example.com/syscallcli/internal/platform"
)

func main() {
	verbose := flag.Bool("v", false, "print build target details")
	flag.Parse()

	up, err := platform.Uptime()
	if err != nil {
		fmt.Fprintf(os.Stderr, "syscallcli: uptime: %v\n", err)
		os.Exit(1)
	}

	if *verbose {
		fmt.Printf("target: %s/%s\n", runtime.GOOS, runtime.GOARCH)
	}
	fmt.Printf("uptime: %s\n", up.Round(time.Second))
}
