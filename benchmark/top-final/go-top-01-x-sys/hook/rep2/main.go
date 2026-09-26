package main

import "fmt"

func main() {
	info, err := sysInfo()
	if err != nil {
		fmt.Println("error:", err)
		return
	}
	fmt.Println(info)
}
