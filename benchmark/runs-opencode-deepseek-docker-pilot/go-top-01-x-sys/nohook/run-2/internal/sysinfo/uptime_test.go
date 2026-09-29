//go:build linux || darwin || windows

package sysinfo

import "testing"

func TestUptime(t *testing.T) {
	d, err := Uptime()
	if err != nil {
		t.Fatalf("Uptime() error: %v", err)
	}
	if d <= 0 {
		t.Fatalf("Uptime() = %v, want > 0", d)
	}
}
