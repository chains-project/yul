//go:build linux || darwin

package sysinfo

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func get() (Info, error) {
	var u unix.Utsname
	if err := unix.Uname(&u); err != nil {
		return Info{}, fmt.Errorf("uname: %w", err)
	}
	return Info{
		OS:      unix.ByteSliceToString(u.Sysname[:]),
		Release: unix.ByteSliceToString(u.Release[:]),
		Machine: unix.ByteSliceToString(u.Machine[:]),
	}, nil
}
