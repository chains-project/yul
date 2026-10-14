package stack_test

import (
	"testing"

	. "gopkg.in/check.v1"

	"example.com/myproject/stack"
)

// Hook gocheck into the standard "go test" runner. One call per package
// runs every suite registered with Suite().
func Test(t *testing.T) { TestingT(t) }

type StackSuite struct {
	setupSuiteCalls int
	stack           *stack.Stack
}

var _ = Suite(&StackSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *StackSuite) SetUpSuite(c *C) {
	s.setupSuiteCalls++
}

// TearDownSuite runs once after all tests in the suite.
func (s *StackSuite) TearDownSuite(c *C) {
	c.Check(s.setupSuiteCalls, Equals, 1)
}

// SetUpTest runs before every test, giving each one a fresh fixture.
func (s *StackSuite) SetUpTest(c *C) {
	s.stack = &stack.Stack{}
	s.stack.Push(1)
	s.stack.Push(2)
}

// TearDownTest runs after every test, even if it failed.
func (s *StackSuite) TearDownTest(c *C) {
	s.stack = nil
}

func (s *StackSuite) TestPopReturnsLastPushed(c *C) {
	v, err := s.stack.Pop()
	c.Assert(err, IsNil)
	c.Check(v, Equals, 2)
	c.Check(s.stack.Len(), Equals, 1)
}

func (s *StackSuite) TestPopEmpty(c *C) {
	s.stack.Pop()
	s.stack.Pop()
	_, err := s.stack.Pop()
	c.Check(err, Equals, stack.ErrEmpty)
}

func (s *StackSuite) TestFixtureIsFresh(c *C) {
	// Proves SetUpTest isolates tests from each other's mutations.
	c.Check(s.stack.Len(), Equals, 2)
}

func (s *StackSuite) TestTempDir(c *C) {
	// c.MkDir returns a directory removed automatically after the test.
	dir := c.MkDir()
	c.Check(dir, Not(Equals), "")
}

func (s *StackSuite) BenchmarkPushPop(c *C) {
	for i := 0; i < c.N; i++ {
		s.stack.Push(i)
		s.stack.Pop()
	}
}
