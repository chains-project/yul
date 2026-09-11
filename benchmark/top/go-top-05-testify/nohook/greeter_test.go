package project

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type mockGreeter struct {
	mock.Mock
}

func (m *mockGreeter) Greet(name string) string {
	args := m.Called(name)
	return args.String(0)
}

func TestSayHello(t *testing.T) {
	m := new(mockGreeter)
	m.On("Greet", "World").Return("Hello, World!")

	got := SayHello(m, "World")

	assert.Equal(t, "Hello, World!", got)
	m.AssertExpectations(t)
}
