package platform

import "testing"

func TestKernelRelease(t *testing.T) {
	r, err := KernelRelease()
	if err == ErrUnsupported {
		t.Skip(err)
	}
	if err != nil {
		t.Fatal(err)
	}
	if r == "" {
		t.Fatal("empty kernel release")
	}
	t.Log(r)
}
