//go:build darwin

package sysinfo

import (
	"time"

	"golang.org/x/sys/unix"
)

func Uptime() (time.Duration, error) {
	tv, err := unix.SysctlTimeval("kern.boottime")
	if err != nil {
		return 0, err
	}
	boot := time.Unix(tv.Sec, int64(tv.Usec)*int64(time.Microsecond))
	return time.Since(boot), nil
}
