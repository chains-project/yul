package notify

import "errors"

type Sender interface {
	Send(to, message string) error
}

type Notifier struct {
	sender Sender
}

func New(sender Sender) *Notifier {
	return &Notifier{sender: sender}
}

func (n *Notifier) Notify(to, name string) error {
	if to == "" {
		return errors.New("recipient is required")
	}
	return n.sender.Send(to, "Hello, "+name+"!")
}
