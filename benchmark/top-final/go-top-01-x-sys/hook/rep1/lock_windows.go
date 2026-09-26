//go:build windows

package main

import (
	"os"

	"golang.org/x/sys/windows"
)

func run() error {
	f, err := os.OpenFile("syscli.lock", os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()

	handle := windows.Handle(f.Fd())
	overlapped := new(windows.Overlapped)
	if err := windows.LockFileEx(handle, windows.LOCKFILE_EXCLUSIVE_LOCK, 0, 1, 0, overlapped); err != nil {
		return err
	}
	defer windows.UnlockFileEx(handle, 0, 1, 0, overlapped)

	println("acquired exclusive lock on syscli.lock")
	return nil
}
