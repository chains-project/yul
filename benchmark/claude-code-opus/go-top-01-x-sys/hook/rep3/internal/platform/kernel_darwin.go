package platform

import "golang.org/x/sys/unix"

// KernelRelease returns the running Darwin kernel's release string.
func KernelRelease() (string, error) {
	return unix.Sysctl("kern.osrelease")
}
