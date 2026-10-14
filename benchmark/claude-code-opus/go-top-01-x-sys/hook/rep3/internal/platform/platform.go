// Package platform wraps low-level, OS-specific system calls behind a
// portable API. Each supported OS has its own implementation file selected
// by the Go toolchain's filename suffix (_linux.go, _darwin.go, _windows.go)
// or by //go:build constraints.
//
// Use golang.org/x/sys/unix and golang.org/x/sys/windows rather than the
// frozen standard library "syscall" package.
package platform

import "errors"

// ErrUnsupported is returned on operating systems without an implementation.
var ErrUnsupported = errors.New("platform: operation not supported on this OS")
