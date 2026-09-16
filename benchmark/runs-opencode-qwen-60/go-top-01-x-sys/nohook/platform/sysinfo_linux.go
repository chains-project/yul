//go:build linux

package platform

import (
	"fmt"
	"runtime"

	"golang.org/x/sys/unix"
)

func OS() string {
	return "Linux"
}

func Arch() (string, error) {
	return runtime.GOARCH, nil
}

func OSVersion() (string, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return "", fmt.Errorf("uname: %w", err)
	}
	return fmt.Sprintf("%s %s", unix.ByteSliceToString(uts.Release[:]), unix.ByteSliceToString(uts.Machine[:])), nil
}

func GetPID() (int, error) {
	return unix.Getpid(), nil
}