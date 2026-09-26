package testifydemo

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockNotifier struct {
	mock.Mock
}

func (m *MockNotifier) Notify(message string) error {
	args := m.Called(message)
	return args.Error(0)
}

func TestGreeter_Greet(t *testing.T) {
	notifier := new(MockNotifier)
	notifier.On("Notify", "Hello, World").Return(nil)

	g := &Greeter{Notifier: notifier}
	err := g.Greet("World")

	assert.NoError(t, err)
	notifier.AssertExpectations(t)
}
