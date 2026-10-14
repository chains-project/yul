// Package sysinfo wraps platform-specific system calls behind a common API.
//
// Platform implementations live in files with GOOS suffixes
// (sysinfo_unix.go, sysinfo_windows.go) and use golang.org/x/sys rather
// than the frozen standard-library syscall package.
package sysinfo

// Info describes the running kernel.
type Info struct {
	OS      string
	Release string
	Machine string
}

// Get returns information about the running kernel.
func Get() (Info, error) {
	return get()
}
