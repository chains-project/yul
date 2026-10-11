package testkit_test

import (
	"testing"

	"example.com/testkit"
	"example.com/testkit/mocks"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestRename_UpdatesAndPersists(t *testing.T) {
	repo := mocks.NewMockUserRepository(t)
	repo.EXPECT().
		FindByID(1).
		Return(testkit.User{ID: 1, Name: "old"}, nil).
		Once()
	repo.EXPECT().
		Save(mock.MatchedBy(func(u testkit.User) bool {
			return u.ID == 1 && u.Name == "new"
		})).
		Return(nil).
		Once()

	svc := testkit.NewService(repo)
	got, err := svc.Rename(1, "new")

	require.NoError(t, err)
	assert.Equal(t, testkit.User{ID: 1, Name: "new"}, got)
}

func TestRename_RejectsEmptyName(t *testing.T) {
	repo := mocks.NewMockUserRepository(t)

	svc := testkit.NewService(repo)
	_, err := svc.Rename(1, "")

	assert.ErrorContains(t, err, "name is required")
}

func TestRename_PropagatesRepositoryError(t *testing.T) {
	repo := mocks.NewMockUserRepository(t)
	repo.EXPECT().
		FindByID(99).
		Return(testkit.User{}, testkit.ErrNotFound).
		Once()

	svc := testkit.NewService(repo)
	_, err := svc.Rename(99, "new")

	require.ErrorIs(t, err, testkit.ErrNotFound)
}
