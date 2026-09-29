//go:build !linux && !darwin && !windows

package sysinfo

// Gather reports ErrUnsupported on platforms without a syscall binding.
func Gather() (Info, error) {
	return Info{}, ErrUnsupported
}
