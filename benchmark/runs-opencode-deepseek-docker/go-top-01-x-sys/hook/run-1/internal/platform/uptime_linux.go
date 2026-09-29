//go:build linux

package platform

import (
	"time"

	"golang.org/x/sys/unix"
)

// Uptime reads the sysinfo(2) syscall directly. The standard library exposes
// neither sysinfo nor the raw system uptime, so this drops to x/sys/unix.
func Uptime() (time.Duration, error) {
	var info unix.Sysinfo_t
	if err := unix.Sysinfo(&info); err != nil {
		return 0, err
	}
	return time.Duration(info.Uptime) * time.Second, nil
}
