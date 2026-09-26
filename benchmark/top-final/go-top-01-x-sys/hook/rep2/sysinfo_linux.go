package main

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func sysInfo() (string, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return "", err
	}
	return fmt.Sprintf("linux kernel release: %s", charsToString(uts.Release[:])), nil
}

func charsToString(b []byte) string {
	n := 0
	for n < len(b) && b[n] != 0 {
		n++
	}
	return string(b[:n])
}
