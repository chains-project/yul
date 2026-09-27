//go:build darwin

package platform

import (
	"time"

	"golang.org/x/sys/unix"
)

// Uptime reads kern.boottime via sysctl(3), which the standard library does not
// expose, then subtracts it from the current time.
func Uptime() (time.Duration, error) {
	tv, err := unix.SysctlTimeval("kern.boottime")
	if err != nil {
		return 0, err
	}
	boot := time.Unix(tv.Sec, int64(tv.Usec)*1000)
	return time.Since(boot), nil
}
