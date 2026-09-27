//go:build !linux && !darwin && !windows

package platform

import (
	"errors"
	"time"
)

// ErrUnsupported is returned on platforms without an implementation.
var ErrUnsupported = errors.New("platform: uptime is not implemented on this GOOS")

// Uptime is unavailable on this platform.
func Uptime() (time.Duration, error) {
	return 0, ErrUnsupported
}
