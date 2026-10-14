package platform

import (
	"fmt"

	"golang.org/x/sys/unix"
)

func query() (Info, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return Info{}, fmt.Errorf("uname: %w", err)
	}

	var si unix.Sysinfo_t
	if err := unix.Sysinfo(&si); err != nil {
		return Info{}, fmt.Errorf("sysinfo: %w", err)
	}

	return Info{
		OS:          unix.ByteSliceToString(uts.Sysname[:]),
		Release:     unix.ByteSliceToString(uts.Release[:]),
		Machine:     unix.ByteSliceToString(uts.Machine[:]),
		TotalMemory: uint64(si.Totalram) * uint64(si.Unit),
	}, nil
}
