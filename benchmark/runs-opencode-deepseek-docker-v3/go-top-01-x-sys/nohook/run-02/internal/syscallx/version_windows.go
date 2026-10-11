//go:build windows

package syscallx

import (
	"fmt"
	"unsafe"

	"golang.org/x/sys/windows"
)

// osVersionInfoW mirrors RTL_OSVERSIONINFOW from the Windows DDK.
type osVersionInfoW struct {
	OSVersionInfoSize uint32
	MajorVersion      uint32
	MinorVersion      uint32
	BuildNumber       uint32
	PlatformID        uint32
	CSDVersion        [128]uint16
}

var (
	ntdll             = windows.NewLazySystemDLL("ntdll.dll")
	procRtlGetVersion = ntdll.NewProc("RtlGetVersion")
)

// KernelVersion reports the Windows version obtained from the undocumented
// RtlGetVersion entry point, which, unlike GetVersionEx, is not subject to
// application-compatibility shims.
func KernelVersion() (string, error) {
	info := osVersionInfoW{OSVersionInfoSize: uint32(unsafe.Sizeof(osVersionInfoW{}))}
	ret, _, err := procRtlGetVersion.Call(uintptr(unsafe.Pointer(&info)))
	if ret != 0 {
		return "", fmt.Errorf("RtlGetVersion failed (NTSTATUS 0x%x): %w", ret, err)
	}
	return fmt.Sprintf("Windows %d.%d build %d",
		info.MajorVersion, info.MinorVersion, info.BuildNumber), nil
}
