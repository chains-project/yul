package main

import (
	"fmt"
	"os"

	"example.com/syscallcli/internal/syscallx"
)

func main() {
	info, err := syscallx.Get()
	if err != nil {
		fmt.Fprintln(os.Stderr, "syscallcli:", err)
		os.Exit(1)
	}

	fmt.Printf("uptime:       %ds\n", info.UptimeSeconds)
	fmt.Printf("total memory: %d bytes\n", info.TotalMemory)
	fmt.Printf("free memory:  %d bytes\n", info.FreeMemory)
	if info.Load1 > 0 {
		fmt.Printf("load (1m):    %.2f\n", info.Load1)
	}
}
