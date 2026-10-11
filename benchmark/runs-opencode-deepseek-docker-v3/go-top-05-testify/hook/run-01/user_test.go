package testkit

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

type mockStore struct {
	mock.Mock
}

func (m *mockStore) FindByID(id int) (*User, error) {
	args := m.Called(id)
	user, _ := args.Get(0).(*User)
	return user, args.Error(1)
}

func TestGreeting(t *testing.T) {
	store := new(mockStore)
	store.On("FindByID", 1).Return(&User{ID: 1, Name: " Ada "}, nil)

	svc := NewUserService(store)

	got, err := svc.Greeting(1)

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	store.AssertExpectations(t)
}

func TestGreeting_NotFound(t *testing.T) {
	store := new(mockStore)
	store.On("FindByID", 99).Return(nil, ErrUserNotFound)

	svc := NewUserService(store)

	_, err := svc.Greeting(99)

	assert.ErrorIs(t, err, ErrUserNotFound)
}

func TestGreeting_StoreFailure(t *testing.T) {
	store := new(mockStore)
	wantErr := errors.New("database down")
	store.On("FindByID", mock.Anything).Return(nil, wantErr)

	svc := NewUserService(store)

	_, err := svc.Greeting(7)

	require.Error(t, err)
	assert.EqualError(t, err, wantErr.Error())
	store.AssertCalled(t, "FindByID", 7)
}
