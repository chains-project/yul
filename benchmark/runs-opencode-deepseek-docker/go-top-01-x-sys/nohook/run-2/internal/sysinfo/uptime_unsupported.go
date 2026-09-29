//go:build !linux && !darwin && !windows

package sysinfo

import "time"

func Uptime() (time.Duration, error) {
	return 0, ErrUnsupported
}
