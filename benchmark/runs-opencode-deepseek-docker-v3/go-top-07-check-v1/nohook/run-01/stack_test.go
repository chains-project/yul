package testkit

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) {
	TestingT(t)
}

var _ = Suite(&StackSuite{})

type StackSuite struct {
	stack *Stack
}

func (s *StackSuite) SetUpSuite(c *C) {
	c.Log("one-time suite fixture setup")
}

func (s *StackSuite) TearDownSuite(c *C) {
	c.Log("one-time suite fixture teardown")
}

func (s *StackSuite) SetUpTest(c *C) {
	s.stack = &Stack{}
}

func (s *StackSuite) TearDownTest(c *C) {
	s.stack = nil
}

func (s *StackSuite) TestPush(c *C) {
	s.stack.Push(1)
	s.stack.Push(2)
	c.Assert(s.stack.Len(), Equals, 2)
}

func (s *StackSuite) TestPop(c *C) {
	s.stack.Push(42)
	v, err := s.stack.Pop()
	c.Assert(err, IsNil)
	c.Assert(v, Equals, 42)
	c.Assert(s.stack.Len(), Equals, 0)
}

func (s *StackSuite) TestPopEmpty(c *C) {
	_, err := s.stack.Pop()
	c.Assert(err, Equals, ErrEmpty)
}
