package native

import (
	"runtime"
	"time"
)

type Platform struct {
	OS   string
	Arch string
}

func Current() Platform {
	return Platform{OS: runtime.GOOS, Arch: runtime.GOARCH}
}

func Uptime() (time.Duration, error) {
	return uptime()
}
