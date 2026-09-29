//go:build linux

package platform

import "golang.org/x/sys/unix"

// Info reports host details using the uname(2) system call.
func Info() (SystemInfo, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return SystemInfo{}, err
	}
	return SystemInfo{
		OS:      unix.ByteSliceToString(uts.Sysname[:]),
		Release: unix.ByteSliceToString(uts.Release[:]),
		Version: unix.ByteSliceToString(uts.Version[:]),
		Machine: unix.ByteSliceToString(uts.Machine[:]),
	}, nil
}
