// Package platform exposes host details gathered through low-level system
// calls that the Go standard library does not wrap.
//
// Each supported operating system provides its own Info implementation in a
// file guarded by a build constraint. The exported API is identical across
// platforms, so callers never need to be aware of the underlying mechanism.
package platform

// SystemInfo describes the host operating system.
type SystemInfo struct {
	OS      string `json:"os"`
	Release string `json:"release"`
	Version string `json:"version"`
	Machine string `json:"machine"`
}
