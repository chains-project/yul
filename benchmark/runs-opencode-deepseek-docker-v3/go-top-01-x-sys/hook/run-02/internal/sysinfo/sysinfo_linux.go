//go:build linux

package sysinfo

import "golang.org/x/sys/unix"

// TotalMemory returns the total amount of physical memory, in bytes.
//
// The standard library has no equivalent; this invokes the raw sysinfo(2)
// system call, whose totals are expressed in multiples of the returned unit.
func TotalMemory() (uint64, error) {
	var info unix.Sysinfo_t
	if err := unix.Sysinfo(&info); err != nil {
		return 0, err
	}
	return info.Totalram * uint64(info.Unit), nil
}
