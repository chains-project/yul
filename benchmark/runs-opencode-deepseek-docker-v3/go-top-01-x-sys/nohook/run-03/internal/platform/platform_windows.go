//go:build windows

package platform

import (
	"runtime"
	"strconv"
	"unsafe"

	"golang.org/x/sys/windows"
)

// rtlOSVersionInfo mirrors RTL_OSVERSIONINFOW from the Windows DDK.
type rtlOSVersionInfo struct {
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

// Query calls ntdll!RtlGetVersion. Unlike GetVersionEx, it is not subject to
// application-compatibility manifest shimming, and the resulting version
// information is not surfaced by the standard library.
func Query() (Info, error) {
	var vi rtlOSVersionInfo
	vi.OSVersionInfoSize = uint32(unsafe.Sizeof(vi))
	ret, _, _ := procRtlGetVersion.Call(uintptr(unsafe.Pointer(&vi)))
	if ret != 0 {
		return Info{}, windows.Errno(ret)
	}
	release := strconv.Itoa(int(vi.MajorVersion)) + "." +
		strconv.Itoa(int(vi.MinorVersion)) + "." +
		strconv.Itoa(int(vi.BuildNumber))
	return Info{
		OS:      "windows",
		Release: release,
		Machine: runtime.GOARCH,
		Extra:   windows.UTF16ToString(vi.CSDVersion[:]),
	}, nil
}
