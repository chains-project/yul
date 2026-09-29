package notify

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

type mockSender struct {
	mock.Mock
}

func (m *mockSender) Send(to, message string) error {
	args := m.Called(to, message)
	return args.Error(0)
}

func TestNotify_SendsMessage(t *testing.T) {
	sender := new(mockSender)
	sender.On("Send", "ada@example.com", "Hello, Ada!").Return(nil)

	require.NoError(t, New(sender).Notify("ada@example.com", "Ada"))
	sender.AssertExpectations(t)
}

func TestNotify_RequiresRecipient(t *testing.T) {
	err := New(new(mockSender)).Notify("", "Ada")

	require.Error(t, err)
	assert.EqualError(t, err, "recipient is required")
}

func TestNotify_PropagatesSendError(t *testing.T) {
	wantErr := errors.New("smtp down")
	sender := new(mockSender)
	sender.On("Send", mock.Anything, mock.Anything).Return(wantErr)

	err := New(sender).Notify("ada@example.com", "Ada")

	assert.ErrorIs(t, err, wantErr)
	sender.AssertExpectations(t)
}
