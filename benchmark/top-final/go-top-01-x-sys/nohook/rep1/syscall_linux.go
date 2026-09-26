package main

import (
	"fmt"
	"time"

	"golang.org/x/sys/unix"
)

// SystemLoad reports how long the system has been running, via uname/sysinfo,
// a syscall the standard library doesn't expose.
func SystemLoad() (string, error) {
	var info unix.Sysinfo_t
	if err := unix.Sysinfo(&info); err != nil {
		return "", err
	}
	uptime := time.Duration(info.Uptime) * time.Second
	return fmt.Sprintf("uptime: %s", uptime), nil
}
