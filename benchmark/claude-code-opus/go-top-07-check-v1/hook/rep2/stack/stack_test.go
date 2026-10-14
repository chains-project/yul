package stack

import (
	"os"
	"path/filepath"
	"testing"

	. "gopkg.in/check.v1"
)

// Test hooks gocheck into the standard "go test" runner.
// Only one such function is needed per package.
func Test(t *testing.T) { TestingT(t) }

// StackSuite groups related tests and holds shared fixtures.
type StackSuite struct {
	fixtureDir string // created once per suite
	stack      *Stack // fresh for every test
}

var _ = Suite(&StackSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *StackSuite) SetUpSuite(c *C) {
	// c.MkDir returns a temp directory removed automatically after the suite.
	s.fixtureDir = c.MkDir()
	err := os.WriteFile(filepath.Join(s.fixtureDir, "seed.txt"), []byte("1 2 3"), 0o644)
	c.Assert(err, IsNil)
}

// TearDownSuite runs once after all tests in the suite.
func (s *StackSuite) TearDownSuite(c *C) {}

// SetUpTest runs before each test.
func (s *StackSuite) SetUpTest(c *C) {
	s.stack = &Stack{}
	s.stack.Push(1)
	s.stack.Push(2)
}

// TearDownTest runs after each test.
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
	c.Assert(err, Equals, ErrEmpty)
}

func (s *StackSuite) TestFixtureFileExists(c *C) {
	data, err := os.ReadFile(filepath.Join(s.fixtureDir, "seed.txt"))
	c.Assert(err, IsNil)
	c.Check(string(data), Equals, "1 2 3")
}

func (s *StackSuite) BenchmarkPushPop(c *C) {
	st := &Stack{}
	for i := 0; i < c.N; i++ {
		st.Push(i)
		st.Pop()
	}
}
