//go:build linux || darwin

package platform

import (
	"os"

	"golang.org/x/sys/unix"
)

// GetInfo returns kernel information via uname(2).
func GetInfo() (Info, error) {
	var u unix.Utsname
	if err := unix.Uname(&u); err != nil {
		return Info{}, err
	}
	return Info{
		Name:    unix.ByteSliceToString(u.Sysname[:]),
		Release: unix.ByteSliceToString(u.Release[:]),
		Version: unix.ByteSliceToString(u.Version[:]),
	}, nil
}

// TermSize returns the terminal dimensions of f via ioctl(TIOCGWINSZ).
func TermSize(f *os.File) (cols, rows int, err error) {
	ws, err := unix.IoctlGetWinsize(int(f.Fd()), unix.TIOCGWINSZ)
	if err != nil {
		return 0, 0, err
	}
	return int(ws.Col), int(ws.Row), nil
}
