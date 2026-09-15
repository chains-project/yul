//go:build linux || darwin

package main

import "golang.org/x/sys/unix"

// diskFree returns the free and total bytes available on the filesystem
// containing path, via the statfs(2) syscall.
func diskFree(path string) (free, total uint64, err error) {
	var stat unix.Statfs_t
	if err := unix.Statfs(path, &stat); err != nil {
		return 0, 0, err
	}
	free = uint64(stat.Bavail) * uint64(stat.Bsize)
	total = uint64(stat.Blocks) * uint64(stat.Bsize)
	return free, total, nil
}
