//go:build darwin

package syscallx

import (
	"time"
	"unsafe"

	"golang.org/x/sys/unix"
)

func Get() (Info, error) {
	raw, err := unix.SysctlRaw("kern.boottime")
	if err != nil {
		return Info{}, err
	}
	if len(raw) < int(unsafe.Sizeof(unix.Timeval{})) {
		return Info{}, unix.EINVAL
	}

	boot := *(*unix.Timeval)(unsafe.Pointer(&raw[0]))
	info := Info{UptimeSeconds: uint64(time.Since(time.Unix(0, unix.TimevalToNsec(boot))).Seconds())}

	if total, err := unix.SysctlUint64("hw.memsize"); err == nil {
		info.TotalMemory = total
	}
	if freePages, err := unix.SysctlUint32("vm.page_free_count"); err == nil {
		info.FreeMemory = uint64(unix.Getpagesize()) * uint64(freePages)
	}

	return info, nil
}
