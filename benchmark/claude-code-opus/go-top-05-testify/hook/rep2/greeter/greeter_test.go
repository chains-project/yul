package greeter

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

func (m *mockStore) Name(id int) (string, error) {
	args := m.Called(id)
	return args.String(0), args.Error(1)
}

func TestGreet(t *testing.T) {
	store := new(mockStore)
	store.On("Name", 42).Return("Ada", nil).Once()

	got, err := Greeter{Store: store}.Greet(42)

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	store.AssertExpectations(t)
}

func TestGreetStoreError(t *testing.T) {
	errNotFound := errors.New("not found")
	store := new(mockStore)
	store.On("Name", 7).Return("", errNotFound)

	_, err := Greeter{Store: store}.Greet(7)

	assert.ErrorIs(t, err, errNotFound)
	store.AssertExpectations(t)
}
