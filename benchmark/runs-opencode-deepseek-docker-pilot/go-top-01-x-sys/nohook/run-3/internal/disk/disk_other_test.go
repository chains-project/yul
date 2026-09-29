//go:build !linux && !darwin && !windows

package disk

import "testing"

func TestFreeUnsupported(t *testing.T) {
	if _, _, err := Free("."); err != ErrUnsupported {
		t.Fatalf("Free(.) error = %v, want ErrUnsupported", err)
	}
}
