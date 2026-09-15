//go:build linux || darwin

package main

import (
	"bytes"
	"fmt"

	"golang.org/x/sys/unix"
)

func platformInfo() (string, error) {
	var uname unix.Utsname
	if err := unix.Uname(&uname); err != nil {
		return "", err
	}
	sysname := string(bytes.TrimRight(uname.Sysname[:], "\x00"))
	release := string(bytes.TrimRight(uname.Release[:], "\x00"))
	return fmt.Sprintf("%s %s", sysname, release), nil
}
