package myapp

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAdd(t *testing.T) {
	result := Add(2, 3)
	assert.Equal(t, 5, result, "2 + 3 should equal 5")
	assert.NotEqual(t, 4, result, "2 + 3 should not equal 4")
	assert.True(t, result > 0, "result should be positive")
}