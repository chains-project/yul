package stack_test

import (
	"os"
	"path/filepath"
	"testing"

	. "gopkg.in/check.v1"

	"example.com/project/stack"
)

// Test hooks gocheck into the standard "go test" runner. One per package.
func Test(t *testing.T) { TestingT(t) }

// StackSuite demonstrates gocheck's fixture lifecycle:
//
//	SetUpSuite    - once, before any test in the suite
//	SetUpTest     - before each test
//	TearDownTest  - after each test
//	TearDownSuite - once, after all tests in the suite
type StackSuite struct {
	dir   string       // suite-wide fixture
	stack *stack.Stack // per-test fixture
}

var _ = Suite(&StackSuite{})

func (s *StackSuite) SetUpSuite(c *C) {
	// c.MkDir returns a temp dir that gocheck removes automatically.
	s.dir = c.MkDir()
}

func (s *StackSuite) TearDownSuite(c *C) {}

func (s *StackSuite) SetUpTest(c *C) {
	s.stack = &stack.Stack{}
	s.stack.Push(1)
	s.stack.Push(2)
}

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
	for s.stack.Len() > 0 {
		_, err := s.stack.Pop()
		c.Assert(err, IsNil)
	}
	_, err := s.stack.Pop()
	c.Check(err, Equals, stack.ErrEmpty)
	c.Check(err, ErrorMatches, "stack: empty")
}

func (s *StackSuite) TestFixtureIsFreshPerTest(c *C) {
	// SetUpTest runs before every test, so mutations elsewhere don't leak.
	c.Check(s.stack.Len(), Equals, 2)
}

func (s *StackSuite) TestSuiteDir(c *C) {
	path := filepath.Join(s.dir, "data.txt")
	c.Assert(os.WriteFile(path, []byte("hello"), 0o644), IsNil)
	b, err := os.ReadFile(path)
	c.Assert(err, IsNil)
	c.Check(string(b), Equals, "hello")
}

func (s *StackSuite) BenchmarkPushPop(c *C) {
	st := &stack.Stack{}
	for i := 0; i < c.N; i++ {
		st.Push(i)
		_, _ = st.Pop()
	}
}
