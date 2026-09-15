package project

// Greeter produces a greeting for a name.
type Greeter interface {
	Greet(name string) string
}

func SayHello(g Greeter, name string) string {
	return g.Greet(name)
}
