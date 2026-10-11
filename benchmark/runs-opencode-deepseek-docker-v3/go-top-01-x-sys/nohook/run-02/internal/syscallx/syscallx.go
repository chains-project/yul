// Package syscallx provides thin wrappers around operating-system syscalls
// that are not exposed by the Go standard library.
//
// The implementation is split into files guarded by build constraints:
//
//	version_unix.go     //go:build unix
//	version_windows.go  //go:build windows
//	version_other.go    //go:build !unix && !windows
//
// The standard library intentionally exposes a small, portable slice of each
// platform's system-call interface. Anything outside that slice belongs in a
// platform-specific file like the ones in this package. The [golang.org/x/sys]
// module supplies stable, generated bindings for the common cases:
//
//   - golang.org/x/sys/unix    on Linux, macOS, the BSDs, Solaris, ...
//   - golang.org/x/sys/windows on Windows
//
// When x/sys lacks a binding as well, call the raw instruction directly:
//
//   - Unix:    unix.Syscall / unix.Syscall6 / unix.RawSyscall
//   - Windows: windows.NewLazySystemDLL(...).NewProc(...).Call(...)
//
// [golang.org/x/sys]: https://pkg.go.dev/golang.org/x/sys
package syscallx
