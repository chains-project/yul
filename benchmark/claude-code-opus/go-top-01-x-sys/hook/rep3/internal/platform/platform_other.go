//go:build !linux && !darwin && !windows

package platform

import "os"

func KernelRelease() (string, error) { return "", ErrUnsupported }

func TerminalSize(*os.File) (cols, rows int, err error) { return 0, 0, ErrUnsupported }
