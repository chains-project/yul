//go:build windows

package platform

import (
	"time"

	"golang.org/x/sys/windows"
)

// kernel32 procedures are resolved lazily so the process only binds the symbols
// it actually uses. GetTickCount64 is not surfaced by the standard library.
var (
	kernel32         = windows.NewLazySystemDLL("kernel32.dll")
	procGetTickCount = kernel32.NewProc("GetTickCount64")
)

// Uptime calls GetTickCount64, which returns milliseconds since boot and never
// fails.
func Uptime() (time.Duration, error) {
	ms, _, _ := procGetTickCount.Call()
	return time.Duration(ms) * time.Millisecond, nil
}
