package greeter

import "fmt"

type Notifier interface {
	Notify(recipient, message string) error
}

type Greeter struct {
	notifier Notifier
}

func New(notifier Notifier) *Greeter {
	return &Greeter{notifier: notifier}
}

func (g *Greeter) Greet(name string) (string, error) {
	message := fmt.Sprintf("Hello, %s!", name)
	if err := g.notifier.Notify(name, message); err != nil {
		return "", err
	}
	return message, nil
}
