// Package sysinfo exposes low-level system information that is not available
// through the Go standard library. Each operating system provides its own
// implementation behind a build tag, so callers use a single, portable API on
// Linux, macOS, and Windows.
//
// To add new information, add a function here (or a new common file), then
// implement it in the matching sysinfo_<goos>.go file using golang.org/x/sys.
package sysinfo

import "fmt"

// HumanBytes formats n as a human-readable quantity using binary prefixes.
func HumanBytes(n uint64) string {
	const unit = 1024
	if n < unit {
		return fmt.Sprintf("%d B", n)
	}
	div, exp := uint64(unit), 0
	for v := n / unit; v >= unit; v /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %ciB", float64(n)/float64(div), "KMGTPE"[exp])
}
