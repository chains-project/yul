//go:build windows

package native

import (
	"time"

	"golang.org/x/sys/windows"
)

var (
	kernel32           = windows.NewLazySystemDLL("kernel32.dll")
	procGetTickCount64 = kernel32.NewProc("GetTickCount64")
)

func uptime() (time.Duration, error) {
	millis, _, _ := procGetTickCount64.Call()
	return time.Duration(millis) * time.Millisecond, nil
}
