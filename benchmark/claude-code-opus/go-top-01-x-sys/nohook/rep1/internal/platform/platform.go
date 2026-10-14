// Package platform wraps OS-specific system calls behind a common API.
//
// Each supported OS has its own file selected by Go's filename and
// //go:build constraints:
//
//	platform_unix.go     linux, darwin (shared POSIX calls)
//	platform_linux.go    linux only
//	platform_darwin.go   darwin only
//	platform_windows.go  windows only
//	platform_other.go    fallback returning ErrUnsupported
//
// Use golang.org/x/sys/{unix,windows} rather than the frozen standard
// library syscall package.
package platform

import "errors"

// ErrUnsupported is returned on operating systems without an implementation.
var ErrUnsupported = errors.New("not supported on this platform")

// Info describes the running operating system kernel.
type Info struct {
	Name    string // e.g. "Linux", "Darwin", "Windows"
	Release string // kernel release / build number
	Version string // detailed version string
}
