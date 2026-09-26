package testifysetup

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type Store interface {
	Get(key string) (string, error)
}

type MockStore struct {
	mock.Mock
}

func (m *MockStore) Get(key string) (string, error) {
	args := m.Called(key)
	return args.String(0), args.Error(1)
}

func TestMockStore_Get(t *testing.T) {
	store := new(MockStore)
	store.On("Get", "hello").Return("world", nil)

	value, err := store.Get("hello")

	assert.NoError(t, err)
	assert.Equal(t, "world", value)
	store.AssertExpectations(t)
}
