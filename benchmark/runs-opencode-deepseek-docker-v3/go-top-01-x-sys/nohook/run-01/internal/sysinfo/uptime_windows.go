//go:build windows

package sysinfo

import (
	"time"

	"golang.org/x/sys/windows"
)

var procGetTickCount64 = windows.NewLazySystemDLL("kernel32.dll").NewProc("GetTickCount64")

func Uptime() (time.Duration, error) {
	if err := procGetTickCount64.Find(); err != nil {
		return 0, err
	}
	ms, _, _ := procGetTickCount64.Call()
	return time.Duration(ms) * time.Millisecond, nil
}
