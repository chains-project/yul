//go:build windows

package sysinfo

// systemInfo mirrors the SYSTEM_INFO structure filled by GetNativeSystemInfo.
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

// memoryStatusEx mirrors the MEMORYSTATUSEX structure used by
// GlobalMemoryStatusEx.
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

//sys	getNativeSystemInfo(info *systemInfo) = kernel32.GetNativeSystemInfo
//sys	globalMemoryStatusEx(buf *memoryStatusEx) (err error) = kernel32.GlobalMemoryStatusEx
//sys	getTickCount64() (ms uint64) = kernel32.GetTickCount64
