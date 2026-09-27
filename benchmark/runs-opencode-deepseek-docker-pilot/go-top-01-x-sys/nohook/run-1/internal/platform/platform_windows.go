//go:build windows

package platform

import (
	"fmt"
	"runtime"

	"golang.org/x/sys/windows"
)

// Info reports host details using the ntdll RtlGetNtVersionNumbers call,
// which bypasses the shim layer used by the standard library's version APIs.
func Info() (SystemInfo, error) {
	major, minor, build := windows.RtlGetNtVersionNumbers()
	build &= 0xffff // RtlGetNtVersionNumbers sets the high bits on some builds.
	return SystemInfo{
		OS:      "Windows",
		Release: fmt.Sprintf("%d.%d", major, minor),
		Version: fmt.Sprintf("build %d", build),
		Machine: runtime.GOARCH,
	}, nil
}
