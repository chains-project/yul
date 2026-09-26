package project

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type Greeter interface {
	Greet(name string) string
}

type GreeterMock struct {
	mock.Mock
}

func (m *GreeterMock) Greet(name string) string {
	args := m.Called(name)
	return args.String(0)
}

func TestGreeterMock(t *testing.T) {
	m := new(GreeterMock)
	m.On("Greet", "World").Return("Hello, World")

	result := m.Greet("World")

	assert.Equal(t, "Hello, World", result)
	m.AssertExpectations(t)
}
