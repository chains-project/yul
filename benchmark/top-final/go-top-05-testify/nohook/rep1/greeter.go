package testifydemo

type Notifier interface {
	Notify(message string) error
}

type Greeter struct {
	Notifier Notifier
}

func (g *Greeter) Greet(name string) error {
	return g.Notifier.Notify("Hello, " + name)
}
