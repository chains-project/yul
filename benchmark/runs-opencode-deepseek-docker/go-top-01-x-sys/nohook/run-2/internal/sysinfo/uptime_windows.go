//go:build windows

package sysinfo

import (
	"time"

	"golang.org/x/sys/windows"
)

func Uptime() (time.Duration, error) {
	return windows.DurationSinceBoot(), nil
}
