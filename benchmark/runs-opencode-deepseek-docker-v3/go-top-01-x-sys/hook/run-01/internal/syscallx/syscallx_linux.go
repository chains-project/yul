//go:build linux

package syscallx

import "golang.org/x/sys/unix"

func Get() (Info, error) {
	var si unix.Sysinfo_t
	if err := unix.Sysinfo(&si); err != nil {
		return Info{}, err
	}

	unit := uint64(si.Unit)
	if unit == 0 {
		unit = 1
	}

	info := Info{
		UptimeSeconds: uint64(si.Uptime),
		TotalMemory:   si.Totalram * unit,
		FreeMemory:    si.Freeram * unit,
	}

	info.Load1 = float64(si.Loads[0]) / 65536.0

	return info, nil
}
