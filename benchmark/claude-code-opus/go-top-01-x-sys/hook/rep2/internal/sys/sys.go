// Package sys wraps platform-specific system calls behind a portable API.
//
// Implementations live in build-constrained files:
//   - sys_unix.go    (linux, darwin) using golang.org/x/sys/unix
//   - sys_windows.go (windows)       using golang.org/x/sys/windows
//   - sys_other.go   (everything else) returning ErrUnsupported
package sys

import "errors"

// ErrUnsupported is returned on platforms without an implementation.
var ErrUnsupported = errors.ErrUnsupported
