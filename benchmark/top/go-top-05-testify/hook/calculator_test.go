package calculator

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockAdder struct {
	mock.Mock
}

func (m *MockAdder) Add(a, b int) int {
	args := m.Called(a, b)
	return args.Int(0)
}

func TestCalculator_Sum(t *testing.T) {
	mockAdder := new(MockAdder)
	mockAdder.On("Add", 2, 3).Return(5)

	calc := NewCalculator(mockAdder)
	result := calc.Sum(2, 3)

	assert.Equal(t, 5, result)
	mockAdder.AssertExpectations(t)
}
