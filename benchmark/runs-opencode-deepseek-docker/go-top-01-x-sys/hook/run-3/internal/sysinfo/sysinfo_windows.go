//go:build windows

package sysinfo

import (
	"fmt"
	"strconv"
	"unsafe"

	"golang.org/x/sys/windows"
)

// Gather reports Windows system information. Identity comes from the NT
// routine RtlGetVersion and the kernel32 calls bound in syscall_windows.go;
// the standard library exposes none of them.
func Gather() (Info, error) {
	name, err := windows.ComputerName()
	if err != nil {
		return Info{}, err
	}

	info := Info{
		Hostname: name,
		Uptime:   -1,
		Details:  map[string]string{},
	}

	ver := windows.RtlGetVersion()
	info.Kernel = fmt.Sprintf("%d.%d.%d", ver.MajorVersion, ver.MinorVersion, ver.BuildNumber)

	var si systemInfo
	getNativeSystemInfo(&si)
	info.Arch = archName(si.ProcessorArchitecture)
	info.Details["cpus"] = strconv.FormatUint(uint64(si.NumberOfProcessors), 10)
	info.Details["page_size"] = strconv.FormatUint(uint64(si.PageSize), 10)

	// Unlike x/sys, the standard library has no memory-status binding.
	mem := memoryStatusEx{Length: uint32(unsafe.Sizeof(memoryStatusEx{}))}
	if err := globalMemoryStatusEx(&mem); err == nil {
		info.Memory = mem.TotalPhys
	}
	if ms := getTickCount64(); ms > 0 {
		info.Uptime = int64(ms / 1000)
	}

	return info, nil
}

func archName(a uint16) string {
	switch a {
	case 0:
		return "x86"
	case 5:
		return "arm"
	case 6:
		return "ia64"
	case 9:
		return "amd64"
	case 12:
		return "arm64"
	default:
		return strconv.FormatUint(uint64(a), 10)
	}
}
