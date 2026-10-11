//go:build !unix && !windows

package syscallx

import "errors"

// KernelVersion is unavailable on this platform.
func KernelVersion() (string, error) {
	return "", errors.New("syscallx: kernel version lookup is not implemented for this platform")
}
