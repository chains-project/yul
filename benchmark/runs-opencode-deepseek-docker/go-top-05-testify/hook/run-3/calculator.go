package testkit

import "errors"

var ErrDivideByZero = errors.New("divide by zero")

type Calculator struct{}

func (Calculator) Divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	return a / b, nil
}
