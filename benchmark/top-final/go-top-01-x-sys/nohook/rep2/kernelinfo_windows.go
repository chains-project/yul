//go:build windows

package main

import (
	"fmt"

	"golang.org/x/sys/windows"
)

// kernelInfo reports the Windows kernel version via RtlGetVersion, which has
// no equivalent in the standard library.
func kernelInfo() (string, error) {
	info := windows.RtlGetVersion()
	return fmt.Sprintf("Windows %d.%d.%d", info.MajorVersion, info.MinorVersion, info.BuildNumber), nil
}
