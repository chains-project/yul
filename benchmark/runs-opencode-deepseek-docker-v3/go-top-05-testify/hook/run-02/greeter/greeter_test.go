package greeter_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"example.com/testkit/greeter"
)

// mockNameProvider is a testify mock implementing greeter.NameProvider.
type mockNameProvider struct {
	mock.Mock
}

func (m *mockNameProvider) Name(ctx context.Context, id string) (string, error) {
	args := m.Called(ctx, id)
	return args.String(0), args.Error(1)
}

func TestGreeter_Greet(t *testing.T) {
	names := new(mockNameProvider)
	names.On("Name", mock.Anything, "42").Return("Ada", nil)

	got, err := greeter.New(names).Greet(context.Background(), "42")

	require.NoError(t, err)
	assert.Equal(t, "Hello, Ada!", got)
	names.AssertExpectations(t)
}

func TestGreeter_GreetError(t *testing.T) {
	names := new(mockNameProvider)
	names.On("Name", mock.Anything, "42").Return("", errors.New("not found"))

	got, err := greeter.New(names).Greet(context.Background(), "42")

	require.Error(t, err)
	assert.Empty(t, got)
	assert.ErrorContains(t, err, "resolve name for \"42\": not found")
	names.AssertExpectations(t)
}

func TestGreeter_GreetTable(t *testing.T) {
	tests := []struct {
		name   string
		userID string
		person string
		want   string
	}{
		{name: "ascii name", userID: "1", person: "Ada", want: "Hello, Ada!"},
		{name: "unicode name", userID: "2", person: "日本", want: "Hello, 日本!"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			names := new(mockNameProvider)
			names.On("Name", mock.Anything, tt.userID).Return(tt.person, nil)

			got, err := greeter.New(names).Greet(context.Background(), tt.userID)

			require.NoError(t, err)
			assert.Equal(t, tt.want, got)
			names.AssertExpectations(t)
		})
	}
}
