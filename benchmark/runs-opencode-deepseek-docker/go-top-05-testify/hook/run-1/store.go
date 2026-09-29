package project

import "errors"

// ErrNotFound is returned when a requested record does not exist.
var ErrNotFound = errors.New("not found")

// Store loads records by id.
type Store interface {
	Get(id string) (string, error)
}

// Service contains the greeting business logic.
type Service struct {
	store Store
}

// NewService wires a Service to its Store dependency.
func NewService(s Store) *Service {
	return &Service{store: s}
}

// Greet loads a name from the Store and greets it.
func (s *Service) Greet(id string) (string, error) {
	name, err := s.store.Get(id)
	if err != nil {
		return "", err
	}
	return "hello " + name, nil
}
