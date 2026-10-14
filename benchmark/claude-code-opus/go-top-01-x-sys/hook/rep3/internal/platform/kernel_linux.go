package platform

import "golang.org/x/sys/unix"

// KernelRelease returns the running kernel's release string (uname -r).
func KernelRelease() (string, error) {
	var u unix.Utsname
	if err := unix.Uname(&u); err != nil {
		return "", err
	}
	return unix.ByteSliceToString(u.Release[:]), nil
}
