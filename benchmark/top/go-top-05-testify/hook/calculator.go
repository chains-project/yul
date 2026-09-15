package calculator

// Adder abstracts addition so it can be mocked in tests.
type Adder interface {
	Add(a, b int) int
}

type Calculator struct {
	adder Adder
}

func NewCalculator(adder Adder) *Calculator {
	return &Calculator{adder: adder}
}

func (c *Calculator) Sum(a, b int) int {
	return c.adder.Add(a, b)
}
