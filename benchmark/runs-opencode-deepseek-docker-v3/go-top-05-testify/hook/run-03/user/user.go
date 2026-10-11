//go:generate go run go.uber.org/mock/mockgen -source=user.go -destination=mock_repository.go -package=user

package user

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("user not found")

type User struct {
	ID   int
	Name string
}

// Repository is the dependency we will mock in tests.
type Repository interface {
	FindByID(id int) (*User, error)
}

type Service struct {
	repo Repository
}

func NewService(repo Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) Greeting(id int) (string, error) {
	u, err := s.repo.FindByID(id)
	if err != nil {
		return "", err
	}
	if u == nil {
		return "", ErrNotFound
	}
	return fmt.Sprintf("Hello, %s!", u.Name), nil
}
