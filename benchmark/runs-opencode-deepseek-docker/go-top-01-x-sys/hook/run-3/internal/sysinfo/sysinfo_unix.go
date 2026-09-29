//go:build linux || darwin

package sysinfo

import "bytes"

// utsName converts a NUL-terminated utsname(2) character array to a Go string.
// The standard library does not expose uname(2) at all, so the fields are
// decoded by hand from the array x/sys returns.
func utsName(b []byte) string {
	if i := bytes.IndexByte(b, 0); i >= 0 {
		b = b[:i]
	}
	return string(b)
}
