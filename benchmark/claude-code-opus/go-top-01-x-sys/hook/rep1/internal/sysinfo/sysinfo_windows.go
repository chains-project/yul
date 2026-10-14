//go:build windows

package sysinfo

import (
	"fmt"
	"unsafe"

	"golang.org/x/sys/windows"
)

// APIs not wrapped by x/sys/windows are loaded lazily from System32.
// NewLazySystemDLL (unlike NewLazyDLL) is safe against DLL preloading attacks.
var (
	modkernel32             = windows.NewLazySystemDLL("kernel32.dll")
	procGetNativeSystemInfo = modkernel32.NewProc("GetNativeSystemInfo")
)

// systemInfo mirrors the Win32 SYSTEM_INFO struct.
type systemInfo struct {
	ProcessorArchitecture     uint16
	Reserved                  uint16
	PageSize                  uint32
	MinimumApplicationAddress uintptr
	MaximumApplicationAddress uintptr
	ActiveProcessorMask       uintptr
	NumberOfProcessors        uint32
	ProcessorType             uint32
	AllocationGranularity     uint32
	ProcessorLevel            uint16
	ProcessorRevision         uint16
}

const (
	processorArchitectureIntel = 0
	processorArchitectureARM64 = 12
	processorArchitectureAMD64 = 9
)

func get() (Info, error) {
	// RtlGetVersion reports the true OS version, unlike GetVersionEx,
	// which lies to processes without a compatibility manifest.
	v := windows.RtlGetVersion()

	if err := procGetNativeSystemInfo.Find(); err != nil {
		return Info{}, fmt.Errorf("GetNativeSystemInfo: %w", err)
	}
	var si systemInfo
	// GetNativeSystemInfo returns void, so there is no error to check.
	procGetNativeSystemInfo.Call(uintptr(unsafe.Pointer(&si)))

	return Info{
		OS:      "Windows",
		Release: fmt.Sprintf("%d.%d.%d", v.MajorVersion, v.MinorVersion, v.BuildNumber),
		Machine: archName(si.ProcessorArchitecture),
	}, nil
}

func archName(a uint16) string {
	switch a {
	case processorArchitectureAMD64:
		return "x86_64"
	case processorArchitectureARM64:
		return "arm64"
	case processorArchitectureIntel:
		return "x86"
	default:
		return fmt.Sprintf("unknown(%d)", a)
	}
}
