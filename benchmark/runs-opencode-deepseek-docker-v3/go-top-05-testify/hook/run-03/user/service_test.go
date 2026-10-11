package user

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

type mockRepository struct {
	mock.Mock
}

func (m *mockRepository) FindByID(id int) (*User, error) {
	args := m.Called(id)
	u, _ := args.Get(0).(*User)
	return u, args.Error(1)
}

func TestServiceGreeting(t *testing.T) {
	repo := new(mockRepository)
	repo.On("FindByID", 1).Return(&User{ID: 1, Name: "Ada"}, nil)

	svc := NewService(repo)
	got, err := svc.Greeting(1)

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	repo.AssertExpectations(t)
}

func TestServiceGreetingNotFound(t *testing.T) {
	repo := new(mockRepository)
	repo.On("FindByID", 42).Return(nil, ErrNotFound)

	svc := NewService(repo)
	_, err := svc.Greeting(42)

	require.ErrorIs(t, err, ErrNotFound)
	repo.AssertExpectations(t)
}
