package testkit_test

import (
	"testing"

	testkit "example.com/testkit"
	check "gopkg.in/check.v1"
)

// CounterSuite groups related tests. gocheck runs every method whose name
// begins with "Test".
type CounterSuite struct {
	counter *testkit.Counter
}

// Register the suite with gocheck.
var _ = check.Suite(&CounterSuite{})

// SetUpSuite runs once before any test in the suite. Use it for expensive
// fixtures shared across all tests.
func (s *CounterSuite) SetUpSuite(c *check.C) {
	c.Log("SetUpSuite: allocating shared fixture resources")
}

// TearDownSuite runs once after every test in the suite has finished.
func (s *CounterSuite) TearDownSuite(c *check.C) {
	c.Log("TearDownSuite: releasing shared fixture resources")
}

// SetUpTest runs before each individual test, providing a fresh fixture.
func (s *CounterSuite) SetUpTest(c *check.C) {
	s.counter = &testkit.Counter{}
}

// TearDownTest runs after each individual test so state cannot leak.
func (s *CounterSuite) TearDownTest(c *check.C) {
	s.counter = nil
}

func (s *CounterSuite) TestStartsAtZero(c *check.C) {
	c.Assert(s.counter.Value(), check.Equals, 0)
}

func (s *CounterSuite) TestInc(c *check.C) {
	s.counter.Inc()
	s.counter.Inc()
	c.Assert(s.counter.Value(), check.Equals, 2)
}

func (s *CounterSuite) TestAdd(c *check.C) {
	s.counter.Add(41)
	c.Assert(s.counter.Value(), check.Equals, 41)
}

func (s *CounterSuite) TestReset(c *check.C) {
	s.counter.Add(10)
	s.counter.Reset()
	c.Assert(s.counter.Value(), check.Equals, 0)
}

// Test bridges gocheck into the standard `go test` runner.
func Test(t *testing.T) {
	check.TestingT(t)
}
