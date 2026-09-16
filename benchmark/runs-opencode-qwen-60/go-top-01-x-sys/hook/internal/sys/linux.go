//go:build linux

package sys

import (
	"fmt"
	"runtime"
	"syscall"
)

func getDefaultInfo() (*SystemInfo, error) {
	var buf syscall.Utsname
	if err := syscall.Uname(&buf); err != nil {
		return nil, fmt.Errorf("uname: %w", err)
	}
	return &SystemInfo{
		Platform: runtime.GOOS,
		OS:       fmt.Sprintf("%s %s", int8ToString(buf.Release[:]), int8ToString(buf.Machine[:])),
		Arch:     runtime.GOARCH,
	}, nil
}

func int8ToString(b []int8) string {
	n := 0
	for n < len(b) && b[n] != 0 {
		n++
	}
	s := make([]byte, n)
	for i := 0; i < n; i++ {
		s[i] = byte(b[i])
	}
	return string(s)
}