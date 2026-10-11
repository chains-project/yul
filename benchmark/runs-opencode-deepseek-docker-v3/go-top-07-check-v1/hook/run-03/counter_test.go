package gosuite

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Hook into the standard `go test` runner.
func Test(t *testing.T) { TestingT(t) }

// CounterSuite bundles tests that share fixtures and lifecycle hooks.
type CounterSuite struct {
	counter *Counter
}

// Register the suite with gocheck.
var _ = Suite(&CounterSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *CounterSuite) SetUpSuite(c *C) {
	c.Log("setting up CounterSuite")
}

// TearDownSuite runs once after all tests in the suite have finished.
func (s *CounterSuite) TearDownSuite(c *C) {
	c.Log("tearing down CounterSuite")
}

// SetUpTest runs before each individual test, giving every test a fresh fixture.
func (s *CounterSuite) SetUpTest(c *C) {
	s.counter = NewCounter()
}

// TearDownTest runs after each individual test.
func (s *CounterSuite) TearDownTest(c *C) {
	s.counter.Reset()
}

func (s *CounterSuite) TestStartsAtZero(c *C) {
	c.Assert(s.counter.Value(), Equals, 0)
}

func (s *CounterSuite) TestInc(c *C) {
	s.counter.Inc()
	c.Assert(s.counter.Value(), Equals, 1)
}

func (s *CounterSuite) TestAdd(c *C) {
	s.counter.Add(5)
	c.Assert(s.counter.Value(), Equals, 5)
}

func (s *CounterSuite) TestFixtureIsIsolated(c *C) {
	c.Assert(s.counter.Value(), Equals, 0, Commentf("SetUpTest should reset the fixture"))
}
