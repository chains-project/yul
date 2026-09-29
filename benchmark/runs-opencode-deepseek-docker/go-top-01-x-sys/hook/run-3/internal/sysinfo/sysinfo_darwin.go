//go:build darwin

package sysinfo

import (
	"strconv"
	"strings"
	"time"

	"golang.org/x/sys/unix"
)

// Gather reports macOS system information. It uses uname(2) for identity and
// the sysctl(3) MIB for uptime, memory and hardware details; the standard
// library exposes neither.
func Gather() (Info, error) {
	var uts unix.Utsname
	if err := unix.Uname(&uts); err != nil {
		return Info{}, err
	}

	info := Info{
		Hostname: utsName(uts.Nodename[:]),
		Kernel:   strings.TrimSpace(utsName(uts.Release[:]) + " " + utsName(uts.Version[:])),
		Arch:     utsName(uts.Machine[:]),
		Uptime:   -1,
		Details:  map[string]string{},
	}

	if mem, err := unix.SysctlUint64("hw.memsize"); err == nil {
		info.Memory = mem
	}
	if boot, err := unix.SysctlTimeval("kern.boottime"); err == nil {
		info.Uptime = time.Now().Unix() - boot.Sec
	}
	if cpus, err := unix.SysctlUint32("hw.ncpu"); err == nil {
		info.Details["cpus"] = strconv.FormatUint(uint64(cpus), 10)
	}
	if model, err := unix.Sysctl("hw.model"); err == nil {
		info.Details["model"] = model
	}

	return info, nil
}
