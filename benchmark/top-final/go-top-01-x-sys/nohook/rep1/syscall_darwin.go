package main

import (
	"fmt"
	"time"

	"golang.org/x/sys/unix"
)

// SystemLoad reports monotonic clock time since boot, via clock_gettime,
// a syscall the standard library doesn't expose.
func SystemLoad() (string, error) {
	var ts unix.Timespec
	if err := unix.ClockGettime(unix.CLOCK_UPTIME_RAW, &ts); err != nil {
		return "", err
	}
	uptime := time.Duration(ts.Sec)*time.Second + time.Duration(ts.Nsec)
	return fmt.Sprintf("uptime: %s", uptime), nil
}
