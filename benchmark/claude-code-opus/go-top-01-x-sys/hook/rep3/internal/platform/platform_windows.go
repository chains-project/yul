package platform

import (
	"fmt"
	"os"

	"golang.org/x/sys/windows"
)

// KernelRelease returns the Windows version as major.minor.build.
// RtlGetVersion reports the true version regardless of app manifest.
func KernelRelease() (string, error) {
	v := windows.RtlGetVersion()
	return fmt.Sprintf("%d.%d.%d", v.MajorVersion, v.MinorVersion, v.BuildNumber), nil
}

// TerminalSize returns the width and height of the console attached to f.
func TerminalSize(f *os.File) (cols, rows int, err error) {
	var info windows.ConsoleScreenBufferInfo
	if err := windows.GetConsoleScreenBufferInfo(windows.Handle(f.Fd()), &info); err != nil {
		return 0, 0, err
	}
	w := info.Window
	return int(w.Right-w.Left) + 1, int(w.Bottom-w.Top) + 1, nil
}
