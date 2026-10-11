package greeter_test

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"example.com/cleanertests/greeter"
)

type mockNameStore struct {
	mock.Mock
}

func (m *mockNameStore) Lookup(id string) (string, error) {
	args := m.Called(id)
	return args.String(0), args.Error(1)
}

func TestGreeter_Greet(t *testing.T) {
	store := new(mockNameStore)
	store.On("Lookup", "42").Return("Ada", nil)

	got, err := greeter.New(store).Greet("42")

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	store.AssertExpectations(t)
}

func TestGreeter_Greet_NotFound(t *testing.T) {
	store := new(mockNameStore)
	store.On("Lookup", "unknown").Return("", greeter.ErrNotFound)

	got, err := greeter.New(store).Greet("unknown")

	assert.ErrorIs(t, err, greeter.ErrNotFound)
	assert.Empty(t, got)
	store.AssertExpectations(t)
}

func TestGreeter_Greet_UnexpectedError(t *testing.T) {
	store := new(mockNameStore)
	store.On("Lookup", mock.Anything).Return("", errors.New("boom"))

	_, err := greeter.New(store).Greet("any")

	assert.ErrorContains(t, err, "boom")
	store.AssertExpectations(t)
}
