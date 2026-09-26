package sysinfo

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func Get() (string, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return "", err
	}
	return fmt.Sprintf("%s %s (%s)", charsToString(uts.Sysname[:]), charsToString(uts.Release[:]), charsToString(uts.Machine[:])), nil
}

func charsToString(b []byte) string {
	n := 0
	for n < len(b) && b[n] != 0 {
		n++
	}
	return string(b[:n])
}
