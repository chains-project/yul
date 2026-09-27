//go:build !linux && !darwin && !windows

package platform

import (
	"errors"
	"fmt"
	"runtime"
)

// ErrUnsupported is returned on operating systems without a low-level
// implementation.
var ErrUnsupported = errors.New("platform: unsupported operating system")

// Info returns ErrUnsupported on platforms that have no implementation.
func Info() (SystemInfo, error) {
	return SystemInfo{}, fmt.Errorf("%w: %s", ErrUnsupported, runtime.GOOS)
}
