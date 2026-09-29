package suitekit

import "errors"

// ErrDivideByZero is returned by Divide when the divisor is zero.
var ErrDivideByZero = errors.New("divide by zero")

// Add returns the sum of a and b.
func Add(a, b int) int {
	return a + b
}

// Divide returns a divided by b, or ErrDivideByZero when b is zero.
func Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	return a / b, nil
}
