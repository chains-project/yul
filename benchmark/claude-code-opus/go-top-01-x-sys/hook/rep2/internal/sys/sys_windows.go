//go:build windows

package sys

import (
	"os"

	"golang.org/x/sys/windows"
)

// TerminalSize returns the column and row count of the console attached to f.
func TerminalSize(f *os.File) (cols, rows int, err error) {
	var info windows.ConsoleScreenBufferInfo
	if err := windows.GetConsoleScreenBufferInfo(windows.Handle(f.Fd()), &info); err != nil {
		return 0, 0, err
	}
	w := info.Window
	return int(w.Right-w.Left) + 1, int(w.Bottom-w.Top) + 1, nil
}
