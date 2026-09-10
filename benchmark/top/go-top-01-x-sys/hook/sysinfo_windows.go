//go:build windows

package main

import (
	"fmt"

	"golang.org/x/sys/windows"
)

func platformInfo() (string, error) {
	v := windows.RtlGetVersion()
	return fmt.Sprintf("Windows %d.%d build %d", v.MajorVersion, v.MinorVersion, v.BuildNumber), nil
}
