// Package disk reports filesystem statistics using platform system calls that
// are not exposed by the Go standard library.
//
// The exported API is declared in platform-specific files, each guarded by a
// build constraint:
//
//	disk_unix.go     //go:build linux || darwin
//	disk_windows.go  //go:build windows
//	disk_other.go    //go:build !linux && !darwin && !windows
//
// Adding another raw system call follows the same shape: declare the exported
// function once per supported platform, and provide an unsupported fallback so
// the package still compiles everywhere.
//
// Prefer the typed wrappers in golang.org/x/sys. When a call has no wrapper,
// invoke it directly:
//
//   - Linux/macOS: unix.Syscall, unix.Syscall6 or unix.RawSyscall with the
//     SYS_* constant, or unix.Sysctl for macOS/BSD kernel parameters.
//   - Windows: windows.NewLazySystemDLL("...").
//     NewProc("...").Call(...) for calls without a generated wrapper.
package disk

import "errors"

// ErrUnsupported reports that the current operating system has no
// implementation of an operation.
var ErrUnsupported = errors.New("disk: operation not supported on this platform")
