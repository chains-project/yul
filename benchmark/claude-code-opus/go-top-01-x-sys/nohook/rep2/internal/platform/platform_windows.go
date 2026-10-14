package platform

import (
	"fmt"
	"runtime"
	"unsafe"

	"golang.org/x/sys/windows"
)

// GlobalMemoryStatusEx is not wrapped by x/sys/windows, so bind it directly.
// NewLazySystemDLL only loads from System32, preventing DLL search-path hijacking.
var (
	modkernel32              = windows.NewLazySystemDLL("kernel32.dll")
	procGlobalMemoryStatusEx = modkernel32.NewProc("GlobalMemoryStatusEx")
)

// memoryStatusEx mirrors MEMORYSTATUSEX.
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

func query() (Info, error) {
	// RtlGetVersion reports the true version, unlike GetVersionEx which is
	// subject to manifest-based compatibility shims.
	v := windows.RtlGetVersion()

	ms := memoryStatusEx{Length: uint32(unsafe.Sizeof(memoryStatusEx{}))}
	if err := procGlobalMemoryStatusEx.Find(); err != nil {
		return Info{}, fmt.Errorf("GlobalMemoryStatusEx: %w", err)
	}
	r, _, err := procGlobalMemoryStatusEx.Call(uintptr(unsafe.Pointer(&ms)))
	if r == 0 {
		return Info{}, fmt.Errorf("GlobalMemoryStatusEx: %w", err)
	}

	return Info{
		OS:          "Windows",
		Release:     fmt.Sprintf("%d.%d.%d", v.MajorVersion, v.MinorVersion, v.BuildNumber),
		Machine:     runtime.GOARCH,
		TotalMemory: ms.TotalPhys,
	}, nil
}
