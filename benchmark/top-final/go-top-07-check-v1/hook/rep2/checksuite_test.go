package checksuite

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type CounterSuite struct {
	counter int
}

var _ = Suite(&CounterSuite{})

func (s *CounterSuite) SetUpSuite(c *C) {
	// runs once before all tests in the suite
}

func (s *CounterSuite) TearDownSuite(c *C) {
	// runs once after all tests in the suite
}

func (s *CounterSuite) SetUpTest(c *C) {
	s.counter = 0
}

func (s *CounterSuite) TearDownTest(c *C) {
	s.counter = 0
}

func (s *CounterSuite) TestIncrement(c *C) {
	s.counter++
	c.Assert(s.counter, Equals, 1)
}

func (s *CounterSuite) TestStartsAtZero(c *C) {
	c.Assert(s.counter, Equals, 0)
}
