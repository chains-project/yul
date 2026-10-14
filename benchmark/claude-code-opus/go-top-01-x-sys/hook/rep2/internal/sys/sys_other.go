//go:build !linux && !darwin && !windows

package sys

import "os"

// TerminalSize is not implemented on this platform.
func TerminalSize(f *os.File) (cols, rows int, err error) {
	return 0, 0, ErrUnsupported
}
