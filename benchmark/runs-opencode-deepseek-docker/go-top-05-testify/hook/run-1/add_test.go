package project

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAdd(t *testing.T) {
	require.Equal(t, 4, Add(2, 2))
	assert.Equal(t, 0, Add(-1, 1))
	assert.Equal(t, -3, Add(-1, -2))
}
