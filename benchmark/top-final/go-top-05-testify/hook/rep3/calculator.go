package testifydemo

type Notifier interface {
	Notify(message string) error
}

type Calculator struct {
	notifier Notifier
}

func NewCalculator(notifier Notifier) *Calculator {
	return &Calculator{notifier: notifier}
}

func (c *Calculator) Add(a, b int) (int, error) {
	result := a + b
	if err := c.notifier.Notify("computed sum"); err != nil {
		return 0, err
	}
	return result, nil
}
