//go:build linux || darwin

package sys

import (
	"os"

	"golang.org/x/sys/unix"
)

// TerminalSize returns the column and row count of the terminal attached to f.
func TerminalSize(f *os.File) (cols, rows int, err error) {
	ws, err := unix.IoctlGetWinsize(int(f.Fd()), unix.TIOCGWINSZ)
	if err != nil {
		return 0, 0, err
	}
	return int(ws.Col), int(ws.Row), nil
}
