package sysinfo

import "testing"

func TestTotalMemory(t *testing.T) {
	total, err := TotalMemory()
	if err != nil {
		t.Fatalf("TotalMemory: %v", err)
	}
	if total == 0 {
		t.Fatal("TotalMemory returned 0")
	}
}

func TestHumanBytes(t *testing.T) {
	cases := []struct {
		in   uint64
		want string
	}{
		{0, "0 B"},
		{512, "512 B"},
		{1024, "1.0 KiB"},
		{1536, "1.5 KiB"},
		{1024 * 1024, "1.0 MiB"},
		{3 * 1024 * 1024 * 1024, "3.0 GiB"},
	}
	for _, tc := range cases {
		if got := HumanBytes(tc.in); got != tc.want {
			t.Errorf("HumanBytes(%d) = %q, want %q", tc.in, got, tc.want)
		}
	}
}
