//go:build windows

package sys

import (
	"fmt"
	"runtime"
)

// getDefaultInfo returns basic system information on Windows.
// For detailed Windows system calls (registry, services, Win32 APIs),
// use golang.org/x/sys/windows.
func getDefaultInfo() (*SystemInfo, error) {
	return &SystemInfo{
		Platform: runtime.GOOS,
		OS:       fmt.Sprintf("Windows %s", runtime.GOARCH),
		Arch:     runtime.GOARCH,
	}, nil
}