package main

import (
	"fmt"

	"golang.org/x/sys/windows"
)

func sysInfo() (string, error) {
	major, minor, build := windows.RtlGetNtVersionNumbers()
	return fmt.Sprintf("windows version: %d.%d build %d", major, minor, build), nil
}
