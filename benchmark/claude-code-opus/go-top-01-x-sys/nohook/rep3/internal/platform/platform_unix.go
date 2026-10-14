//go:build linux || darwin

package platform

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func info() (SystemInfo, error) {
	var u unix.Utsname
	if err := unix.Uname(&u); err != nil {
		return SystemInfo{}, fmt.Errorf("uname: %w", err)
	}

	up, err := uptime()
	if err != nil {
		return SystemInfo{}, err
	}

	return SystemInfo{
		OS:      unix.ByteSliceToString(u.Sysname[:]),
		Release: unix.ByteSliceToString(u.Release[:]),
		Arch:    unix.ByteSliceToString(u.Machine[:]),
		Uptime:  up,
	}, nil
}
