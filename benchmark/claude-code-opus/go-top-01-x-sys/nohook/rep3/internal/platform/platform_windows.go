package platform

import (
	"fmt"
	"runtime"
	"time"

	"golang.org/x/sys/windows"
)

func info() (SystemInfo, error) {
	// RtlGetVersion reports the real OS version, unlike GetVersionEx, which
	// is subject to manifest-based compatibility shims.
	v := windows.RtlGetVersion()

	return SystemInfo{
		OS:      "Windows",
		Release: fmt.Sprintf("%d.%d.%d", v.MajorVersion, v.MinorVersion, v.BuildNumber),
		Arch:    runtime.GOARCH,
		Uptime:  time.Duration(windows.DurationSinceBoot()).Truncate(time.Second),
	}, nil
}
