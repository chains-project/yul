package platform

import (
	"fmt"
	"time"

	"golang.org/x/sys/unix"
)

func uptime() (time.Duration, error) {
	var si unix.Sysinfo_t
	if err := unix.Sysinfo(&si); err != nil {
		return 0, fmt.Errorf("sysinfo: %w", err)
	}
	return time.Duration(si.Uptime) * time.Second, nil
}
