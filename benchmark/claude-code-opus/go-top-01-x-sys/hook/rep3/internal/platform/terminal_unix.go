//go:build linux || darwin

package platform

import (
	"os"

	"golang.org/x/sys/unix"
)

// TerminalSize returns the width and height of the terminal attached to f.
func TerminalSize(f *os.File) (cols, rows int, err error) {
	ws, err := unix.IoctlGetWinsize(int(f.Fd()), unix.TIOCGWINSZ)
	if err != nil {
		return 0, 0, err
	}
	return int(ws.Col), int(ws.Row), nil
}
