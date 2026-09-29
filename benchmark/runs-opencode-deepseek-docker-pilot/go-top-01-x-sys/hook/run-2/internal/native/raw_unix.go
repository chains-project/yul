//go:build linux || darwin

package native

import "golang.org/x/sys/unix"

func RawSyscall(trap, a1, a2, a3 uintptr) (r1, r2 uintptr, err error) {
	r1, r2, e := unix.Syscall(trap, a1, a2, a3)
	if e != 0 {
		err = e
	}
	return r1, r2, err
}

func RawSyscall6(trap, a1, a2, a3, a4, a5, a6 uintptr) (r1, r2 uintptr, err error) {
	r1, r2, e := unix.Syscall6(trap, a1, a2, a3, a4, a5, a6)
	if e != 0 {
		err = e
	}
	return r1, r2, err
}
