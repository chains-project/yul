//go:build !linux && !darwin && !windows

package platform

import (
	"os"
	"time"
)

func GetInfo() (Info, error)                        { return Info{}, ErrUnsupported }
func TermSize(*os.File) (cols, rows int, err error) { return 0, 0, ErrUnsupported }
func Uptime() (time.Duration, error)                { return 0, ErrUnsupported }
