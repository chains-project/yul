package testkit

import "errors"

// ErrNotFound is returned when a user cannot be located.
var ErrNotFound = errors.New("user not found")

// User is a minimal domain object.
type User struct {
	ID   int
	Name string
}

// UserRepository is the storage dependency of Service.
type UserRepository interface {
	FindByID(id int) (User, error)
	Save(user User) error
}

// Service coordinates user lookups and updates.
type Service struct {
	repo UserRepository
}

// NewService wires a Service to its repository.
func NewService(repo UserRepository) *Service {
	return &Service{repo: repo}
}

// Rename updates the stored name of the user with the given ID.
func (s *Service) Rename(id int, name string) (User, error) {
	if name == "" {
		return User{}, errors.New("name is required")
	}

	user, err := s.repo.FindByID(id)
	if err != nil {
		return User{}, err
	}

	user.Name = name
	if err := s.repo.Save(user); err != nil {
		return User{}, err
	}

	return user, nil
}
