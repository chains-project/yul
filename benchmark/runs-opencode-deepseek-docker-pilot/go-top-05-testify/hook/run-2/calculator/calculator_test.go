package calculator_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"example.com/myapp/calculator"
)

type mockStore struct {
	mock.Mock
}

func (m *mockStore) Get(key string) (int, bool) {
	args := m.Called(key)
	return args.Int(0), args.Bool(1)
}

func (m *mockStore) Save(key string, value int) {
	m.Called(key, value)
}

func TestCalculator_Add(t *testing.T) {
	c := calculator.New(nil)

	assert.Equal(t, 4, c.Add(2, 2))
}

func TestCalculator_AddAndSave(t *testing.T) {
	store := new(mockStore)
	store.On("Save", "total", 7).Return().Once()

	c := calculator.New(store)

	require.Equal(t, 7, c.AddAndSave("total", 3, 4))
	store.AssertExpectations(t)
}
