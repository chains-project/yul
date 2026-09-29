//go:build !linux && !darwin && !windows

package native

import (
	"errors"
	"runtime"
	"time"
)

func uptime() (time.Duration, error) {
	return 0, errors.New("native: uptime is not implemented on " + runtime.GOOS)
}
