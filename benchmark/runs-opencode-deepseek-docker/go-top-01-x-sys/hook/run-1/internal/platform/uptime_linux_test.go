//go:build linux

package platform

import "testing"

func TestUptime(t *testing.T) {
	up, err := Uptime()
	if err != nil {
		t.Fatalf("Uptime: %v", err)
	}
	if up <= 0 {
		t.Fatalf("Uptime = %v, want > 0", up)
	}
}
