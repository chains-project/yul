package calc

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Test hooks gocheck into the standard "go test" runner. One per package.
func Test(t *testing.T) { TestingT(t) }

type AccumulatorSuite struct {
	acc     *Accumulator
	tempDir string
}

var _ = Suite(&AccumulatorSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *AccumulatorSuite) SetUpSuite(c *C) {
	// c.MkDir creates a temp directory that is removed automatically.
	s.tempDir = c.MkDir()
}

// TearDownSuite runs once after all tests in the suite.
func (s *AccumulatorSuite) TearDownSuite(c *C) {}

// SetUpTest runs before each test, giving every test a fresh fixture.
func (s *AccumulatorSuite) SetUpTest(c *C) {
	s.acc = &Accumulator{}
}

// TearDownTest runs after each test, even if the test fails.
func (s *AccumulatorSuite) TearDownTest(c *C) {
	s.acc.Reset()
}

func (s *AccumulatorSuite) TestAddAccumulates(c *C) {
	c.Assert(s.acc.Add(2), Equals, 2)
	c.Assert(s.acc.Add(3), Equals, 5)
}

func (s *AccumulatorSuite) TestFreshFixturePerTest(c *C) {
	c.Check(s.acc.Total(), Equals, 0)
}

func (s *AccumulatorSuite) TestSuiteTempDir(c *C) {
	c.Assert(s.tempDir, Not(Equals), "")
}

// Benchmarks also run within the suite: go test -check.b
func (s *AccumulatorSuite) BenchmarkAdd(c *C) {
	for i := 0; i < c.N; i++ {
		s.acc.Add(1)
	}
}
