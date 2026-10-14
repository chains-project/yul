package platform

import (
	"errors"
	"testing"
)

func TestQuery(t *testing.T) {
	info, err := Query()
	if errors.Is(err, ErrUnsupported) {
		t.Skip(err)
	}
	if err != nil {
		t.Fatal(err)
	}
	if info.OS == "" || info.Release == "" {
		t.Errorf("incomplete info: %+v", info)
	}
	if info.TotalMemory == 0 {
		t.Errorf("TotalMemory = 0")
	}
}
