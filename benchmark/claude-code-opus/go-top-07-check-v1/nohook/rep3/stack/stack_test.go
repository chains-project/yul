package stack_test

import (
	"os"
	"path/filepath"
	"testing"

	. "gopkg.in/check.v1"

	"example.com/project/stack"
)

// Test hooks gocheck into "go test". Needed once per package.
func Test(t *testing.T) { TestingT(t) }

// StackSuite demonstrates suite-level and test-level fixtures.
type StackSuite struct {
	dataDir string       // created once for the whole suite
	s       *stack.Stack // fresh for every test
}

var _ = Suite(&StackSuite{})

// SetUpSuite runs once before any test in the suite.
func (x *StackSuite) SetUpSuite(c *C) {
	// c.MkDir returns a temp dir that gocheck removes automatically.
	x.dataDir = c.MkDir()
	err := os.WriteFile(filepath.Join(x.dataDir, "seed"), []byte("1 2 3"), 0o644)
	c.Assert(err, IsNil)
}

// TearDownSuite runs once after all tests in the suite.
func (x *StackSuite) TearDownSuite(c *C) {}

// SetUpTest runs before each test method.
func (x *StackSuite) SetUpTest(c *C) {
	x.s = &stack.Stack{}
	x.s.Push(1)
	x.s.Push(2)
}

// TearDownTest runs after each test method, even if it failed.
func (x *StackSuite) TearDownTest(c *C) {
	x.s = nil
}

func (x *StackSuite) TestPopReturnsLastPushed(c *C) {
	v, err := x.s.Pop()
	c.Assert(err, IsNil)
	c.Check(v, Equals, 2)
	c.Check(x.s.Len(), Equals, 1)
}

func (x *StackSuite) TestPopEmpty(c *C) {
	x.s.Pop()
	x.s.Pop()
	_, err := x.s.Pop()
	c.Assert(err, Equals, stack.ErrEmpty)
}

func (x *StackSuite) TestFixtureIsolation(c *C) {
	// Each test gets a fresh stack from SetUpTest regardless of what
	// other tests did to theirs.
	c.Check(x.s.Len(), Equals, 2)
}

func (x *StackSuite) TestSuiteFixture(c *C) {
	data, err := os.ReadFile(filepath.Join(x.dataDir, "seed"))
	c.Assert(err, IsNil)
	c.Check(string(data), Equals, "1 2 3")
}

func (x *StackSuite) BenchmarkPushPop(c *C) {
	for i := 0; i < c.N; i++ {
		x.s.Push(i)
		x.s.Pop()
	}
}
