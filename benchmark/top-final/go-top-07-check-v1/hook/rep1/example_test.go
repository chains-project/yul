package gochecktest

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type ExampleSuite struct {
	counter int
}

var _ = Suite(&ExampleSuite{})

func (s *ExampleSuite) SetUpSuite(c *C) {
	// runs once before all tests in the suite
}

func (s *ExampleSuite) TearDownSuite(c *C) {
	// runs once after all tests in the suite
}

func (s *ExampleSuite) SetUpTest(c *C) {
	s.counter = 0
}

func (s *ExampleSuite) TearDownTest(c *C) {
	s.counter = 0
}

func (s *ExampleSuite) TestIncrement(c *C) {
	s.counter++
	c.Assert(s.counter, Equals, 1)
}

func (s *ExampleSuite) TestEquals(c *C) {
	c.Check(1+1, Equals, 2)
}
