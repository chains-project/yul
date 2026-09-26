package main

import (
	"fmt"
	"os"
)

func main() {
	info, err := kernelInfo()
	if err != nil {
		fmt.Fprintln(os.Stderr, "syscli:", err)
		os.Exit(1)
	}
	fmt.Println(info)
}
