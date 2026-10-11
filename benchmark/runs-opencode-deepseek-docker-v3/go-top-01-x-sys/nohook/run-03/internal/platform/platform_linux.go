//go:build linux

package platform

import "golang.org/x/sys/unix"

// Query uses unix.Uname, which wraps the uname(2) syscall. The standard
// library does not expose the full utsname struct, so this is done via
// golang.org/x/sys/unix.
func Query() (Info, error) {
	var u unix.Utsname
	if err := unix.Uname(&u); err != nil {
		return Info{}, err
	}
	return Info{
		OS:      unix.ByteSliceToString(u.Sysname[:]),
		Release: unix.ByteSliceToString(u.Release[:]),
		Machine: unix.ByteSliceToString(u.Machine[:]),
		Extra:   unix.ByteSliceToString(u.Version[:]),
	}, nil
}
