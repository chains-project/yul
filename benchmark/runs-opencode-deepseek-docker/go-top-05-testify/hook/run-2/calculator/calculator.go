package calculator

type Store interface {
	Get(key string) (int, bool)
	Save(key string, value int)
}

type Calculator struct {
	store Store
}

func New(store Store) *Calculator {
	return &Calculator{store: store}
}

func (c *Calculator) Add(a, b int) int {
	return a + b
}

func (c *Calculator) AddAndSave(key string, a, b int) int {
	sum := a + b
	c.store.Save(key, sum)
	return sum
}
