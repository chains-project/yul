package platform

import (
	"fmt"
	"os"
	"time"
	"unsafe"

	"golang.org/x/sys/windows"
)

// GetInfo returns kernel information via RtlGetVersion, which, unlike
// GetVersionEx, is not subject to application-manifest version lying.
func GetInfo() (Info, error) {
	v := windows.RtlGetVersion()
	return Info{
		Name:    "Windows",
		Release: fmt.Sprintf("%d.%d.%d", v.MajorVersion, v.MinorVersion, v.BuildNumber),
		Version: windows.UTF16ToString(v.CsdVersion[:]),
	}, nil
}

// TermSize returns the console window dimensions via GetConsoleScreenBufferInfo.
func TermSize(f *os.File) (cols, rows int, err error) {
	var info windows.ConsoleScreenBufferInfo
	if err := windows.GetConsoleScreenBufferInfo(windows.Handle(f.Fd()), &info); err != nil {
		return 0, 0, err
	}
	w := info.Window
	return int(w.Right-w.Left) + 1, int(w.Bottom-w.Top) + 1, nil
}

// Functions not wrapped by x/sys/windows are loaded lazily. NewLazySystemDLL
// only searches System32, which prevents DLL preloading attacks.
var (
	kernel32           = windows.NewLazySystemDLL("kernel32.dll")
	procGetTickCount64 = kernel32.NewProc("GetTickCount64")
)

// Uptime returns time since boot via GetTickCount64.
func Uptime() (time.Duration, error) {
	if err := procGetTickCount64.Find(); err != nil {
		return 0, err
	}
	lo, hi, _ := procGetTickCount64.Call()
	ms := uint64(lo)
	if unsafe.Sizeof(uintptr(0)) == 4 { // 386: 64-bit result is split across EDX:EAX
		ms |= uint64(hi) << 32
	}
	return time.Duration(ms) * time.Millisecond, nil
}
