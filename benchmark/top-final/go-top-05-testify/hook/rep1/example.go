package project

// Adder is the collaborator that Multiply depends on.
type Adder interface {
	Add(a, b int) int
}

// Multiply doubles-adds b to itself a-1 times via Adder, purely to give
// the example test suite something to assert on and mock.
func Multiply(adder Adder, a, b int) int {
	result := b
	for i := 1; i < a; i++ {
		result = adder.Add(result, b)
	}
	return result
}
