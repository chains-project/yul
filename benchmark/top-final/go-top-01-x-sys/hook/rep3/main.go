package main

import (
	"fmt"
	"os"

	"syscli/sysinfo"
)

func main() {
	info, err := sysinfo.Get()
	if err != nil {
		fmt.Fprintln(os.Stderr, "sysinfo:", err)
		os.Exit(1)
	}
	fmt.Println(info)
}
