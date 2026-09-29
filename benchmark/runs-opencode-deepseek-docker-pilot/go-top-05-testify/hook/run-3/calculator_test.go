package testkit_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	testkit "example.com/testkit"
)

func TestCalculatorDivide(t *testing.T) {
	calc := testkit.Calculator{}

	t.Run("divides evenly", func(t *testing.T) {
		got, err := calc.Divide(10, 2)
		require.NoError(t, err)
		assert.Equal(t, 5.0, got)
	})

	t.Run("rejects zero divisor", func(t *testing.T) {
		_, err := calc.Divide(1, 0)
		require.Error(t, err)
		assert.ErrorIs(t, err, testkit.ErrDivideByZero)
	})
}
