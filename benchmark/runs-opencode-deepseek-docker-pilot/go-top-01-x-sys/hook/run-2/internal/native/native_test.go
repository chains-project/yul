package native_test

import (
	"testing"

	"example.com/syscallkit/internal/native"
)

func TestUptime(t *testing.T) {
	up, err := native.Uptime()
	if err != nil {
		t.Fatalf("Uptime() error = %v", err)
	}
	if up <= 0 {
		t.Fatalf("Uptime() = %v, want > 0", up)
	}
}

func TestCurrent(t *testing.T) {
	p := native.Current()
	if p.OS == "" || p.Arch == "" {
		t.Fatalf("Current() = %+v, want non-empty OS and Arch", p)
	}
}
