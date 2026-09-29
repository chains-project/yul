// Package sysinfo collects operating-system information by invoking kernel
// interfaces that are not reachable through the Go standard library.
//
// The standard library's syscall package intentionally trails the kernel ABI,
// so each platform implementation here reaches for golang.org/x/sys instead:
//
//   - Linux  uses uname(2) and sysinfo(2)      (golang.org/x/sys/unix)
//   - macOS  uses uname(2) and sysctl(3)       (golang.org/x/sys/unix)
//   - Windows uses RtlGetVersion plus kernel32 calls bound with mkwinsyscall
//     (golang.org/x/sys/windows)
//
// Each platform lives in its own file selected by a build constraint, so the
// package compiles (and can be cross-compiled) on all three targets:
//
//	sysinfo_unix.go        //go:build linux || darwin
//	sysinfo_linux.go       //go:build linux
//	sysinfo_darwin.go      //go:build darwin
//	sysinfo_windows.go     //go:build windows
//	sysinfo_unsupported.go //go:build !linux && !darwin && !windows
package sysinfo

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

// ErrUnsupported is returned by Gather on platforms without an implementation.
var ErrUnsupported = errors.New("sysinfo: unsupported platform")

// Info is the platform-independent snapshot returned by Gather. A field is
// left at its zero value when the running kernel does not export it; callers
// should treat Uptime < 0 and Memory == 0 as "unknown".
type Info struct {
	Hostname string            `json:"hostname"`
	Kernel   string            `json:"kernel"`
	Arch     string            `json:"arch"`
	Uptime   int64             `json:"uptime_seconds"`
	Memory   uint64            `json:"memory_bytes"`
	Details  map[string]string `json:"details,omitempty"`
}

// Text renders Info as aligned "key: value" lines for human consumption.
func (i Info) Text() string {
	var b strings.Builder
	fmt.Fprintf(&b, "hostname: %s\n", i.Hostname)
	fmt.Fprintf(&b, "kernel:   %s\n", i.Kernel)
	fmt.Fprintf(&b, "arch:     %s\n", i.Arch)
	if i.Uptime >= 0 {
		fmt.Fprintf(&b, "uptime:   %ds\n", i.Uptime)
	}
	if i.Memory > 0 {
		fmt.Fprintf(&b, "memory:   %s\n", humanBytes(i.Memory))
	}

	keys := make([]string, 0, len(i.Details))
	for k := range i.Details {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Fprintf(&b, "%-9s %s\n", k+":", i.Details[k])
	}
	return b.String()
}

func humanBytes(n uint64) string {
	const unit = 1024
	if n < unit {
		return fmt.Sprintf("%d B", n)
	}
	div, exp := uint64(unit), 0
	for m := n / unit; m >= unit; m /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %ciB", float64(n)/float64(div), "KMGTPE"[exp])
}
