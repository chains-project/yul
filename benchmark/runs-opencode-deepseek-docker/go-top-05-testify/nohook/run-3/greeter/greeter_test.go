package greeter

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/mock/gomock"
)

func TestGreeterGreet(t *testing.T) {
	tests := []struct {
		name string
		hour int
		want string
	}{
		{name: "morning", hour: 9, want: "Good morning, Ada!"},
		{name: "afternoon", hour: 14, want: "Good afternoon, Ada!"},
		{name: "evening", hour: 21, want: "Good evening, Ada!"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			clock := NewMockClock(ctrl)
			clock.EXPECT().Hour(gomock.Any()).Return(tt.hour, nil).Times(1)

			got, err := New(clock).Greet(context.Background(), "Ada")

			require.NoError(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestGreeterGreetClockError(t *testing.T) {
	ctrl := gomock.NewController(t)
	clock := NewMockClock(ctrl)
	clock.EXPECT().Hour(gomock.Any()).Return(0, errors.New("clock unavailable"))

	_, err := New(clock).Greet(context.Background(), "Ada")

	require.Error(t, err)
	assert.ErrorContains(t, err, "clock unavailable")
}
