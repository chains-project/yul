package sysinfo

import "testing"

func TestGet(t *testing.T) {
	info, err := Get()
	if err != nil {
		t.Fatalf("Get: %v", err)
	}
	if info.OS == "" || info.Release == "" || info.Machine == "" {
		t.Errorf("Get returned incomplete info: %+v", info)
	}
}
