// Package platform provides thin wrappers around operating system calls that
// the Go standard library does not expose in a portable way.
//
// The contract for each entry point is documented below and implemented in
// build-tagged files per GOOS. Because the golang.org/x/sys packages are pure
// Go, these calls cross-compile from any host with CGO_ENABLED=0; no cgo and no
// platform toolchain is required.
//
//	func Uptime() (time.Duration, error)
//
// Uptime reports how long the system has been running.
package platform
