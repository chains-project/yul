//go:build darwin

package platform

import "golang.org/x/sys/unix"

// Query reads the kernel identity through the sysctl(3) interface, which gives
// richer values than uname(2) on Darwin. These calls are not part of the
// standard library.
func Query() (Info, error) {
	osType, err := unix.Sysctl("kern.ostype")
	if err != nil {
		return Info{}, err
	}
	release, err := unix.Sysctl("kern.osrelease")
	if err != nil {
		return Info{}, err
	}
	machine, err := unix.Sysctl("hw.machine")
	if err != nil {
		return Info{}, err
	}
	version, err := unix.Sysctl("kern.version")
	if err != nil {
		return Info{}, err
	}
	return Info{
		OS:      osType,
		Release: release,
		Machine: machine,
		Extra:   version,
	}, nil
}
