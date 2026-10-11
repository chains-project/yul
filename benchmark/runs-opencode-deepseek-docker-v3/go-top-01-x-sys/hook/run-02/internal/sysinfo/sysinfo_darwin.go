//go:build darwin

package sysinfo

import "golang.org/x/sys/unix"

// TotalMemory returns the total amount of physical memory, in bytes.
//
// The standard library has no equivalent; this reads the hw.memsize sysctl.
func TotalMemory() (uint64, error) {
	return unix.SysctlUint64("hw.memsize")
}
