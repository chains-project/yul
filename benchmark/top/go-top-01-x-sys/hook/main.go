package main

import (
	"fmt"
	"os"
)

func main() {
	info, err := platformInfo()
	if err != nil {
		fmt.Fprintln(os.Stderr, "systool:", err)
		os.Exit(1)
	}
	fmt.Println(info)
}
