//go:build linux || darwin

package main

import (
	"fmt"

	"golang.org/x/sys/unix"
)

// kernelInfo reports the kernel name/release via uname(2), which has no
// equivalent in the standard library.
func kernelInfo() (string, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return "", fmt.Errorf("uname: %w", err)
	}
	return fmt.Sprintf("%s %s",
		unix.ByteSliceToString(uts.Sysname[:]),
		unix.ByteSliceToString(uts.Release[:])), nil
}
