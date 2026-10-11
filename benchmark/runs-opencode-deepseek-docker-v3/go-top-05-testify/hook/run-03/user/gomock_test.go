package user

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/mock/gomock"
)

func TestServiceGreetingWithGomock(t *testing.T) {
	ctrl := gomock.NewController(t)
	repo := NewMockRepository(ctrl)

	repo.EXPECT().FindByID(1).Return(&User{ID: 1, Name: "Grace"}, nil)

	svc := NewService(repo)
	got, err := svc.Greeting(1)

	require.NoError(t, err)
	assert.Equal(t, "Hello, Grace!", got)
}
