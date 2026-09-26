package main

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func sysInfo() (string, error) {
	rel, err := unix.Sysctl("kern.version")
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("darwin kernel version: %s", rel), nil
}
