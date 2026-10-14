// Package platform wraps OS-specific system calls behind a portable API.
//
// Each supported OS has its own file selected by filename suffix
// (_linux.go, _darwin.go, _windows.go). Use golang.org/x/sys/unix and
// golang.org/x/sys/windows rather than the frozen standard "syscall" package.
package platform

import "errors"

// ErrUnsupported is returned on platforms without an implementation.
var ErrUnsupported = errors.New("platform: unsupported operating system")

// Info describes the host system.
type Info struct {
	OS          string
	Release     string
	Machine     string
	TotalMemory uint64 // bytes
}

// Query returns information about the host obtained via native system calls.
func Query() (Info, error) {
	return query()
}
