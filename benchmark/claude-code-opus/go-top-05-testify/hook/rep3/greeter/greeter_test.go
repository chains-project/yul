package greeter

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// mockNameStore is a testify mock implementing NameStore.
type mockNameStore struct {
	mock.Mock
}

func (m *mockNameStore) DisplayName(userID string) (string, error) {
	args := m.Called(userID)
	return args.String(0), args.Error(1)
}

func TestGreet(t *testing.T) {
	store := new(mockNameStore)
	store.On("DisplayName", "u1").Return("Ada", nil).Once()

	got, err := New(store).Greet("u1")

	require.NoError(t, err) // stop the test immediately on failure
	assert.Equal(t, "Hello, Ada!", got)
	store.AssertExpectations(t)
}

func TestGreetErrors(t *testing.T) {
	lookupErr := errors.New("not found")

	tests := []struct {
		name    string
		retName string
		retErr  error
		wantErr error
	}{
		{name: "store error is wrapped", retErr: lookupErr, wantErr: lookupErr},
		{name: "empty name", retName: "", wantErr: ErrEmptyName},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			store := new(mockNameStore)
			store.On("DisplayName", mock.AnythingOfType("string")).Return(tt.retName, tt.retErr)

			got, err := New(store).Greet("u2")

			assert.ErrorIs(t, err, tt.wantErr)
			assert.Empty(t, got)
			store.AssertExpectations(t)
		})
	}
}
