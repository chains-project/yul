package suitekit

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Test is the sole bridge to the standard testing package. gocheck discovers
// every registered suite through it, so it only needs to exist once per package.
func Test(t *testing.T) { TestingT(t) }

// CalculatorSuite exercises the calculator with gocheck-style fixtures.
//
// Fixture ordering for each test is:
//
//	SetUpSuite -> SetUpTest -> Test... -> TearDownTest -> ... -> TearDownSuite
type CalculatorSuite struct {
	addCalls    int
	divideCalls int
}

// Suite registers the fixture with gocheck.
var _ = Suite(&CalculatorSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *CalculatorSuite) SetUpSuite(c *C) {
	c.Log("setting up CalculatorSuite")
}

// TearDownSuite runs once after every test in the suite has finished.
func (s *CalculatorSuite) TearDownSuite(c *C) {
	c.Log("tearing down CalculatorSuite")
}

// SetUpTest runs before each individual test, giving it a clean slate.
func (s *CalculatorSuite) SetUpTest(c *C) {
	s.addCalls = 0
	s.divideCalls = 0
}

// TearDownTest runs after each individual test for per-test cleanup.
func (s *CalculatorSuite) TearDownTest(c *C) {
	c.Logf("test finished: add=%d divide=%d", s.addCalls, s.divideCalls)
}

func (s *CalculatorSuite) TestAdd(c *C) {
	s.addCalls++
	c.Assert(Add(2, 3), Equals, 5)
	c.Check(Add(-1, 1), Equals, 0)
}

func (s *CalculatorSuite) TestDivide(c *C) {
	s.divideCalls++
	quotient, err := Divide(10, 2)
	c.Assert(err, IsNil)
	c.Assert(quotient, Equals, 5)
}

func (s *CalculatorSuite) TestDivideByZero(c *C) {
	s.divideCalls++
	_, err := Divide(1, 0)
	c.Assert(err, Equals, ErrDivideByZero)
	c.Assert(err, ErrorMatches, "divide by zero")
}
