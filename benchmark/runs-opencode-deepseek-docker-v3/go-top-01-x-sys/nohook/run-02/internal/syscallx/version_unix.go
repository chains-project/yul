//go:build unix

package syscallx

import (
	"strings"

	"golang.org/x/sys/unix"
)

// KernelVersion reports the system name, release, and machine architecture
// obtained from the uname(2) system call.
func KernelVersion() (string, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return "", err
	}

	parts := []string{
		unix.ByteSliceToString(uts.Sysname[:]),
		unix.ByteSliceToString(uts.Release[:]),
		unix.ByteSliceToString(uts.Machine[:]),
	}
	return strings.Join(parts, " "), nil
}
