//go:build linux || darwin || windows

package disk

import "testing"

func TestFree(t *testing.T) {
	total, free, err := Free(".")
	if err != nil {
		t.Fatalf("Free(.): %v", err)
	}
	if total == 0 {
		t.Error("total = 0, want > 0")
	}
	if free > total {
		t.Errorf("free %d > total %d", free, total)
	}
}
