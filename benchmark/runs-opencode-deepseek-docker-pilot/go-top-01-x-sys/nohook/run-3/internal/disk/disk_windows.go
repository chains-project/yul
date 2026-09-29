//go:build windows

package disk

import "golang.org/x/sys/windows"

// Free returns the total and free bytes of the volume that contains path.
// It is implemented with the GetDiskFreeSpaceEx Win32 API via
// golang.org/x/sys/windows.
func Free(path string) (total, free uint64, err error) {
	name, err := windows.UTF16PtrFromString(path)
	if err != nil {
		return 0, 0, err
	}
	var freeToCaller, totalBytes, totalFree uint64
	if err := windows.GetDiskFreeSpaceEx(name, &freeToCaller, &totalBytes, &totalFree); err != nil {
		return 0, 0, err
	}
	return totalBytes, totalFree, nil
}
