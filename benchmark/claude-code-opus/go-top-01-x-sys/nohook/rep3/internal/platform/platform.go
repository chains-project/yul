// Package platform wraps OS-specific system calls behind a common API.
//
// Each supported OS has its own file selected by Go's filename-based build
// constraints (_linux.go, _darwin.go, _windows.go). Code shared by Unix-like
// systems lives in files guarded by //go:build linux || darwin.
//
// System calls go through golang.org/x/sys rather than the standard library's
// syscall package, which is frozen and doesn't get new calls or constants.
package platform

import "time"

// SystemInfo describes the host system.
type SystemInfo struct {
	OS      string
	Release string
	Arch    string
	Uptime  time.Duration
}

// Info returns information about the host system.
func Info() (SystemInfo, error) {
	return info()
}
