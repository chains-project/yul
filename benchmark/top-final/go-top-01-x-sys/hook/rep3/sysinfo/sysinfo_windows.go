package sysinfo

import (
	"fmt"

	"golang.org/x/sys/windows"
)

func Get() (string, error) {
	major, minor, build := windows.RtlGetNtVersionNumbers()
	return fmt.Sprintf("Windows %d.%d (build %d)", major, minor, build), nil
}
