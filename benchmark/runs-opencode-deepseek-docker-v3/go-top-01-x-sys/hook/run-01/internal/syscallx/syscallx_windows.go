//go:build windows

package syscallx

import (
	"unsafe"

	"golang.org/x/sys/windows"
)

var (
	kernel32                 = windows.NewLazySystemDLL("kernel32.dll")
	procGlobalMemoryStatusEx = kernel32.NewProc("GlobalMemoryStatusEx")
	procGetTickCount64       = kernel32.NewProc("GetTickCount64")
)

type memoryStatusEx struct {
	Length               uint32
	MemoryLoad           uint32
	TotalPhys            uint64
	AvailPhys            uint64
	TotalPageFile        uint64
	AvailPageFile        uint64
	TotalVirtual         uint64
	AvailVirtual         uint64
	AvailExtendedVirtual uint64
}

func Get() (Info, error) {
	var mem memoryStatusEx
	mem.Length = uint32(unsafe.Sizeof(mem))

	r1, _, err := procGlobalMemoryStatusEx.Call(uintptr(unsafe.Pointer(&mem)))
	if r1 == 0 {
		return Info{}, err
	}

	tick, _, _ := procGetTickCount64.Call()

	return Info{
		UptimeSeconds: uint64(tick) / 1000,
		TotalMemory:   mem.TotalPhys,
		FreeMemory:    mem.AvailPhys,
	}, nil
}
