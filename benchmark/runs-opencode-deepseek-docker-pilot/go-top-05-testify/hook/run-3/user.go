package testkit

import "errors"

var ErrUserNotFound = errors.New("user not found")

type User struct {
	ID   string
	Name string
}

type UserRepository interface {
	Find(id string) (User, error)
}

type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}

func (s *UserService) DisplayName(id string) (string, error) {
	user, err := s.repo.Find(id)
	if err != nil {
		return "", err
	}
	return user.Name, nil
}
