//go:build linux

package sysinfo

import (
	"strconv"
	"strings"

	"golang.org/x/sys/unix"
)

// Gather reports Linux system information. It uses uname(2) for identity and
// sysinfo(2) for uptime, load average and physical memory; neither call is
// wrapped by the standard library.
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

	var si unix.Sysinfo_t
	if err := unix.Sysinfo(&si); err != nil {
		return info, err
	}

	info.Uptime = si.Uptime
	info.Memory = si.Totalram * uint64(si.Unit)
	info.Details["loadavg"] = strings.TrimSpace(strings.Join([]string{
		strconv.FormatUint(si.Loads[0], 10),
		strconv.FormatUint(si.Loads[1], 10),
		strconv.FormatUint(si.Loads[2], 10),
	}, " "))
	info.Details["procs"] = strconv.FormatUint(uint64(si.Procs), 10)

	return info, nil
}
