//go:build linux

package native

import (
	"time"

	"golang.org/x/sys/unix"
)

func uptime() (time.Duration, error) {
	var info unix.Sysinfo_t
	if err := unix.Sysinfo(&info); err != nil {
		return 0, err
	}
	return time.Duration(info.Uptime) * time.Second, nil
}
