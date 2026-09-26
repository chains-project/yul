package sysinfo

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func Get() (string, error) {
	release, err := unix.Sysctl("kern.osrelease")
	if err != nil {
		return "", err
	}
	machine, err := unix.Sysctl("hw.machine")
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("Darwin %s (%s)", release, machine), nil
}
