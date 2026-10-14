package platform

import (
	"fmt"
	"time"

	"golang.org/x/sys/unix"
)

func uptime() (time.Duration, error) {
	tv, err := unix.SysctlTimeval("kern.boottime")
	if err != nil {
		return 0, fmt.Errorf("sysctl kern.boottime: %w", err)
	}
	boot := time.Unix(tv.Sec, int64(tv.Usec)*int64(time.Microsecond))
	return time.Since(boot).Truncate(time.Second), nil
}
