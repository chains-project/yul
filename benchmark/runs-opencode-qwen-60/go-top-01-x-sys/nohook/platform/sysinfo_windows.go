//go:build windows

package platform

import (
	"fmt"
	"runtime"

	"golang.org/x/sys/windows"
)

func OS() string {
	return "Windows"
}

func Arch() (string, error) {
	return runtime.GOARCH, nil
}

func OSVersion() (string, error) {
	v, err := windows.RtlGetNtVersionNumbers()
	if err != nil {
		return "", fmt.Errorf("RtlGetNtVersionNumbers: %w", err)
	}
	return fmt.Sprintf("Windows NT %d.%d (%s)", v/0x10000, (v%0x10000)/0x100, runtime.GOARCH), nil
}

func GetPID() (int, error) {
	return windows.GetCurrentProcessId(), nil
}