package hook

import "errors"

// ErrNotFound is returned when a key is not found.
var ErrNotFound = errors.New("key not found")

// Store is a simple key-value store for demonstration.
type Store struct {
	data map[string]string
}

// NewStore creates a new Store.
func NewStore() *Store {
	return &Store{
		data: make(map[string]string),
	}
}

// Set adds or updates a key-value pair.
func (s *Store) Set(key, value string) {
	s.data[key] = value
}

// Get retrieves a value by key.
func (s *Store) Get(key string) (string, error) {
	v, ok := s.data[key]
	if !ok {
		return "", ErrNotFound
	}
	return v, nil
}

// Has checks if a key exists.
func (s *Store) Has(key string) bool {
	_, ok := s.data[key]
	return ok
}

// Delete removes a key from the store.
func (s *Store) Delete(key string) {
	delete(s.data, key)
}

// Len returns the number of entries.
func (s *Store) Len() int {
	return len(s.data)
}