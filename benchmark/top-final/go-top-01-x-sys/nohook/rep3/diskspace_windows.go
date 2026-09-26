//go:build windows

package main

import "golang.org/x/sys/windows"

func diskFree(path string) (free, total uint64, err error) {
	var freeBytesAvailable, totalBytes, totalFreeBytes uint64

	pathPtr, err := windows.UTF16PtrFromString(path)
	if err != nil {
		return 0, 0, err
	}

	if err := windows.GetDiskFreeSpaceEx(pathPtr, &freeBytesAvailable, &totalBytes, &totalFreeBytes); err != nil {
		return 0, 0, err
	}

	return freeBytesAvailable, totalBytes, nil
}
