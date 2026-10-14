package platform

import (
	"time"

	"golang.org/x/sys/unix"
)

// Uptime returns time since boot via sysinfo(2).
func Uptime() (time.Duration, error) {
	var si unix.Sysinfo_t
	if err := unix.Sysinfo(&si); err != nil {
		return 0, err
	}
	return time.Duration(si.Uptime) * time.Second, nil
}
