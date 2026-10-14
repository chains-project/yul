package platform

import "testing"

func TestInfo(t *testing.T) {
	info, err := Info()
	if err != nil {
		t.Fatalf("Info() error: %v", err)
	}
	if info.OS == "" || info.Release == "" || info.Arch == "" {
		t.Errorf("Info() returned empty fields: %+v", info)
	}
	if info.Uptime <= 0 {
		t.Errorf("Info() uptime = %v, want > 0", info.Uptime)
	}
}
