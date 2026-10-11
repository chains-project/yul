package testkit

import (
	"errors"
	"strings"
)

var ErrUserNotFound = errors.New("user not found")

type User struct {
	ID   int
	Name string
}

type Store interface {
	FindByID(id int) (*User, error)
}

type UserService struct {
	store Store
}

func NewUserService(store Store) *UserService {
	return &UserService{store: store}
}

func (s *UserService) Greeting(id int) (string, error) {
	user, err := s.store.FindByID(id)
	if err != nil {
		return "", err
	}
	if user == nil {
		return "", ErrUserNotFound
	}
	return "Hello, " + strings.TrimSpace(user.Name) + "!", nil
}
