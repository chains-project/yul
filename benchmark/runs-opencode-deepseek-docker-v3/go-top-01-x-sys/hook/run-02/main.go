package main

import (
	"flag"
	"fmt"
	"os"

	"example.com/sysinfo/internal/sysinfo"
)

func main() {
	asBytes := flag.Bool("bytes", false, "print memory in bytes instead of human-readable units")
	flag.Usage = func() {
		out := flag.CommandLine.Output()
		fmt.Fprintf(out, "usage: %s [flags]\n\n", os.Args[0])
		fmt.Fprintln(out, "Print low-level system information obtained via direct system calls.")
		fmt.Fprintln(out, "\nFlags:")
		flag.PrintDefaults()
	}
	flag.Parse()

	total, err := sysinfo.TotalMemory()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}

	if *asBytes {
		fmt.Printf("total memory: %d bytes\n", total)
		return
	}
	fmt.Printf("total memory: %s\n", sysinfo.HumanBytes(total))
}
