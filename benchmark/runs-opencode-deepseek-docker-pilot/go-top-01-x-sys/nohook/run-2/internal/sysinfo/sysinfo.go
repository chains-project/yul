package sysinfo

import "errors"

var ErrUnsupported = errors.New("sysinfo: operation not supported on this platform")
