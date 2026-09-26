package rep2

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type Greeter interface {
	Greet(name string) string
}

type MockGreeter struct {
	mock.Mock
}

func (m *MockGreeter) Greet(name string) string {
	args := m.Called(name)
	return args.String(0)
}

func TestMockGreeter(t *testing.T) {
	m := new(MockGreeter)
	m.On("Greet", "world").Return("hello world")

	result := m.Greet("world")

	assert.Equal(t, "hello world", result)
	m.AssertExpectations(t)
}
