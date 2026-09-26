package project

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type mockAdder struct {
	mock.Mock
}

func (m *mockAdder) Add(a, b int) int {
	args := m.Called(a, b)
	return args.Int(0)
}

func TestMultiply(t *testing.T) {
	m := new(mockAdder)
	m.On("Add", 2, 2).Return(4)

	result := Multiply(m, 2, 2)

	assert.Equal(t, 4, result)
	m.AssertExpectations(t)
}
