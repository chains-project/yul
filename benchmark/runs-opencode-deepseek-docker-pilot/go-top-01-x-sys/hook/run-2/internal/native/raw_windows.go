//go:build windows

package native

import "golang.org/x/sys/windows"

func NewLazyProc(dll, name string) *windows.LazyProc {
	return windows.NewLazySystemDLL(dll).NewProc(name)
}
