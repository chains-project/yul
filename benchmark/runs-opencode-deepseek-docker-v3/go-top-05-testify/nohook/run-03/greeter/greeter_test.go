package greeter_test

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"example.com/testkit/greeter"
)

type mockNotifier struct {
	mock.Mock
}

func (m *mockNotifier) Notify(recipient, message string) error {
	args := m.Called(recipient, message)
	return args.Error(0)
}

func TestGreeter_Greet(t *testing.T) {
	notifier := new(mockNotifier)
	notifier.On("Notify", "Ada", "Hello, Ada!").Return(nil)

	message, err := greeter.New(notifier).Greet("Ada")

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", message)
	notifier.AssertExpectations(t)
}

func TestGreeter_Greet_NotifierError(t *testing.T) {
	notifier := new(mockNotifier)
	notifier.On("Notify", "Ada", mock.Anything).Return(errors.New("boom"))

	message, err := greeter.New(notifier).Greet("Ada")

	require.Error(t, err)
	assert.Empty(t, message)
	assert.EqualError(t, err, "boom")
	notifier.AssertExpectations(t)
}
