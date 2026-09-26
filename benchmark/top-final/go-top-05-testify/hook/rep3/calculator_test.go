package testifydemo

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type mockNotifier struct {
	mock.Mock
}

func (m *mockNotifier) Notify(message string) error {
	args := m.Called(message)
	return args.Error(0)
}

func TestCalculatorAdd(t *testing.T) {
	notifier := new(mockNotifier)
	notifier.On("Notify", "computed sum").Return(nil)

	calc := NewCalculator(notifier)
	result, err := calc.Add(2, 3)

	assert.NoError(t, err)
	assert.Equal(t, 5, result)
	notifier.AssertExpectations(t)
}

func TestCalculatorAdd_NotifyFails(t *testing.T) {
	notifier := new(mockNotifier)
	notifier.On("Notify", "computed sum").Return(errors.New("notify failed"))

	calc := NewCalculator(notifier)
	_, err := calc.Add(2, 3)

	assert.Error(t, err)
	notifier.AssertExpectations(t)
}
