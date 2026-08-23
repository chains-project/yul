package main

import (
	"fmt"
	"os"

	"github.com/go-resty/resty/v2"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: cli-tool <url>")
		os.Exit(1)
	}

	client := resty.New()
	resp, err := client.R().Get(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, "request failed:", err)
		os.Exit(1)
	}

	fmt.Println("Status:", resp.Status())
	fmt.Println(resp.String())
}
