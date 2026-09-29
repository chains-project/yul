//go:build linux || darwin

package disk

import "golang.org/x/sys/unix"

// Free returns the total and free bytes of the filesystem that contains path.
// It is implemented with the statfs(2) system call via golang.org/x/sys/unix.
func Free(path string) (total, free uint64, err error) {
	var st unix.Statfs_t
	if err := unix.Statfs(path, &st); err != nil {
		return 0, 0, err
	}
	bsize := uint64(st.Bsize)
	return st.Blocks * bsize, st.Bavail * bsize, nil
}
