package main

import (
	"fmt"
	"time"

	"golang.org/x/sys/windows"
)

var (
	kernel32         = windows.NewLazySystemDLL("kernel32.dll")
	procGetTickCount = kernel32.NewProc("GetTickCount64")
)

// SystemLoad reports how long the system has been running, via GetTickCount64,
// a syscall the standard library doesn't expose. GetTickCount64 has no
// documented failure mode, so the syscall's error return is ignored.
func SystemLoad() (string, error) {
	ret, _, _ := procGetTickCount.Call()
	uptime := time.Duration(ret) * time.Millisecond
	return fmt.Sprintf("uptime: %s", uptime), nil
}
