//go:build darwin

package native

import (
	"time"

	"golang.org/x/sys/unix"
)

func uptime() (time.Duration, error) {
	boot, err := unix.SysctlTimeval("kern.boottime")
	if err != nil {
		return 0, err
	}
	return time.Since(time.Unix(boot.Sec, int64(boot.Usec)*1000)), nil
}
