package store

import (
	"encoding/json"
	"errors"
	"os"
	"sync"
)

var ErrNotFound = errors.New("store: key not found")

type Store struct {
	mu   sync.RWMutex
	path string
	data map[string]string
}

func New(path string) *Store {
	return &Store{path: path, data: map[string]string{}}
}

func (s *Store) Load() error {
	b, err := os.ReadFile(s.path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	return json.Unmarshal(b, &s.data)
}

func (s *Store) Save() error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	b, err := json.Marshal(s.data)
	if err != nil {
		return err
	}
	return os.WriteFile(s.path, b, 0o644)
}

func (s *Store) Set(key, value string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.data[key] = value
}

func (s *Store) Get(key string) (string, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	v, ok := s.data[key]
	if !ok {
		return "", ErrNotFound
	}
	return v, nil
}

func (s *Store) Len() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.data)
}
