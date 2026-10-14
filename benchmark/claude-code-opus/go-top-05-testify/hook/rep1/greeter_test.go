package project

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

type mockNameStore struct {
	mock.Mock
}

func (m *mockNameStore) Name(id int) (string, error) {
	args := m.Called(id)
	return args.String(0), args.Error(1)
}

func TestGreet(t *testing.T) {
	store := new(mockNameStore)
	store.On("Name", 42).Return("Ada", nil).Once()

	got, err := Greet(store, 42)

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	store.AssertExpectations(t)
}

func TestGreet_StoreError(t *testing.T) {
	errNotFound := errors.New("not found")
	store := new(mockNameStore)
	store.On("Name", 7).Return("", errNotFound).Once()

	got, err := Greet(store, 7)

	require.ErrorIs(t, err, errNotFound)
	assert.Empty(t, got)
	store.AssertExpectations(t)
}
