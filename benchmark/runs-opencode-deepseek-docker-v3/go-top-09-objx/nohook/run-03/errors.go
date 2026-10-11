package chainmap

import "errors"

// Sentinel errors returned (wrapped) by chain operations.
var (
	// ErrNotFound indicates that a requested key or path segment is absent.
	ErrNotFound = errors.New("chainmap: key not found")
	// ErrIndexOutOfRange indicates that a slice index is out of bounds.
	ErrIndexOutOfRange = errors.New("chainmap: index out of range")
	// ErrTypeMismatch indicates that a value had an unexpected concrete type.
	ErrTypeMismatch = errors.New("chainmap: type mismatch")
)
