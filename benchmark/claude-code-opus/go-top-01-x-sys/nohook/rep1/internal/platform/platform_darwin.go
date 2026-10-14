package platform

import (
	"time"

	"golang.org/x/sys/unix"
)

// Uptime returns time since boot via sysctl(kern.boottime).
func Uptime() (time.Duration, error) {
	tv, err := unix.SysctlTimeval("kern.boottime")
	if err != nil {
		return 0, err
	}
	return time.Since(time.Unix(tv.Unix())).Truncate(time.Second), nil
}
