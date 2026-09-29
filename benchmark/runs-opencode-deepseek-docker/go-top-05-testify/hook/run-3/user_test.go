package testkit_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	testkit "example.com/testkit"
)

type mockUserRepository struct {
	mock.Mock
}

func (m *mockUserRepository) Find(id string) (testkit.User, error) {
	args := m.Called(id)
	return args.Get(0).(testkit.User), args.Error(1)
}

func TestUserServiceDisplayName(t *testing.T) {
	t.Run("returns the stored name and records the lookup", func(t *testing.T) {
		repo := new(mockUserRepository)
		repo.On("Find", "u-1").Return(testkit.User{ID: "u-1", Name: "Ada"}, nil)

		svc := testkit.NewUserService(repo)

		name, err := svc.DisplayName("u-1")
		require.NoError(t, err)
		assert.Equal(t, "Ada", name)
		repo.AssertExpectations(t)
		repo.AssertCalled(t, "Find", "u-1")
	})

	t.Run("propagates lookup errors", func(t *testing.T) {
		repo := new(mockUserRepository)
		repo.On("Find", "missing").Return(testkit.User{}, testkit.ErrUserNotFound)

		svc := testkit.NewUserService(repo)

		_, err := svc.DisplayName("missing")
		require.Error(t, err)
		assert.ErrorIs(t, err, testkit.ErrUserNotFound)
		repo.AssertExpectations(t)
	})
}
