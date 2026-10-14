//go:build !linux && !darwin && !windows

package platform

import (
	"errors"
	"runtime"
)

func info() (SystemInfo, error) {
	return SystemInfo{}, errors.New("unsupported platform: " + runtime.GOOS)
}
