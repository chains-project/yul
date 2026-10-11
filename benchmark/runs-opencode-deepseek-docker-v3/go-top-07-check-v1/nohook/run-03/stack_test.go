package project

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) {
	TestingT(t)
}

type StackSuite struct {
	stack *Stack
}

var _ = Suite(&StackSuite{})

func (s *StackSuite) SetUpSuite(c *C) {
	c.Log("starting StackSuite")
}

func (s *StackSuite) TearDownSuite(c *C) {
	c.Log("finished StackSuite")
}

func (s *StackSuite) SetUpTest(c *C) {
	s.stack = NewStack()
}

func (s *StackSuite) TearDownTest(c *C) {
	s.stack = nil
}

func (s *StackSuite) TestPushIncreasesLength(c *C) {
	s.stack.Push(1)
	s.stack.Push(2)
	c.Assert(s.stack.Len(), Equals, 2)
}

func (s *StackSuite) TestPopReturnsLastPushed(c *C) {
	s.stack.Push(1)
	s.stack.Push(2)

	v, err := s.stack.Pop()
	c.Assert(err, IsNil)
	c.Assert(v, Equals, 2)

	v, err = s.stack.Pop()
	c.Assert(err, IsNil)
	c.Assert(v, Equals, 1)
}

func (s *StackSuite) TestPopEmptyReturnsError(c *C) {
	_, err := s.stack.Pop()
	c.Assert(err, Equals, ErrEmpty)
}
