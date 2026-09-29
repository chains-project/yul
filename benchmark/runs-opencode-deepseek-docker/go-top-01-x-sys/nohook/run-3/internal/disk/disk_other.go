//go:build !linux && !darwin && !windows

package disk

// Free is not implemented on this platform.
func Free(path string) (total, free uint64, err error) {
	return 0, 0, ErrUnsupported
}
