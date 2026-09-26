//go:build linux || darwin

package main

import (
	"os"

	"golang.org/x/sys/unix"
)

func run() error {
	f, err := os.OpenFile("syscli.lock", os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()

	if err := unix.Flock(int(f.Fd()), unix.LOCK_EX); err != nil {
		return err
	}
	defer unix.Flock(int(f.Fd()), unix.LOCK_UN)

	println("acquired exclusive lock on syscli.lock")
	return nil
}
