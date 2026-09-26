package main

import "fmt"

func main() {
	load, err := SystemLoad()
	if err != nil {
		fmt.Println("error:", err)
		return
	}
	fmt.Println(load)
}
