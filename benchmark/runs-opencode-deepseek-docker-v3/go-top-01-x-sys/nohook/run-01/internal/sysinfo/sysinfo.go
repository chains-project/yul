package sysinfo

import "time"

type Info struct {
	Uptime time.Duration
}

func Collect() (Info, error) {
	uptime, err := Uptime()
	if err != nil {
		return Info{}, err
	}
	return Info{Uptime: uptime}, nil
}
