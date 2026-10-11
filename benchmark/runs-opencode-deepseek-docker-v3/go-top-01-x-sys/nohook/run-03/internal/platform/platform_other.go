//go:build !linux && !darwin && !windows

package platform

import "errors"

// ErrUnsupported is returned by Query on platforms without an implementation.
var ErrUnsupported = errors.New("platform: unsupported operating system")

// Query is a stub for operating systems that this tool does not support yet.
func Query() (Info, error) {
	return Info{}, ErrUnsupported
}
