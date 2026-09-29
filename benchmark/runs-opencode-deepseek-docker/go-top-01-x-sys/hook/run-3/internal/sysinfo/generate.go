package sysinfo

// Regenerate the kernel32 bindings used by sysinfo_windows.go. The directive
// lives in an untagged file because go generate skips files excluded by build
// constraints, which would make this a no-op when run on Linux or macOS.
//
//go:generate go run golang.org/x/sys/windows/mkwinsyscall -output zsyscall_windows.go syscall_windows.go
