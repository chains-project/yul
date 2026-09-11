//go:build windows

package main

import "golang.org/x/sys/windows"

// diskFree returns the free and total bytes available on the volume
// containing path, via the GetDiskFreeSpaceEx syscall.
func diskFree(path string) (free, total uint64, err error) {
	pathPtr, err := windows.UTF16PtrFromString(path)
	if err != nil {
		return 0, 0, err
	}

	var freeBytes, totalBytes, totalFreeBytes uint64
	if err := windows.GetDiskFreeSpaceEx(pathPtr, &freeBytes, &totalBytes, &totalFreeBytes); err != nil {
		return 0, 0, err
	}
	return freeBytes, totalBytes, nil
}
