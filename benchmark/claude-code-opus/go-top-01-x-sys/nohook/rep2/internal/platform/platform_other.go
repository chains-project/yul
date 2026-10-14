//go:build !linux && !darwin && !windows

package platform

func query() (Info, error) {
	return Info{}, ErrUnsupported
}
