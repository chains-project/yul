package project

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

type mockStore struct {
	mock.Mock
}

func (m *mockStore) Get(id string) (string, error) {
	args := m.Called(id)
	return args.String(0), args.Error(1)
}

func TestServiceGreet(t *testing.T) {
	store := new(mockStore)
	store.On("Get", "42").Return("world", nil)

	msg, err := NewService(store).Greet("42")
	require.NoError(t, err)
	assert.Equal(t, "hello world", msg)
	store.AssertExpectations(t)
}

func TestServiceGreetNotFound(t *testing.T) {
	store := new(mockStore)
	store.On("Get", "missing").Return("", ErrNotFound)

	_, err := NewService(store).Greet("missing")
	assert.ErrorIs(t, err, ErrNotFound)
	store.AssertExpectations(t)
}
