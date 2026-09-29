package calculator

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Test hooks the gocheck runner into the standard `go test` entry point.
func Test(t *testing.T) { TestingT(t) }

// CalculatorSuite groups every test that shares the calculator fixture.
type CalculatorSuite struct {
	calc     *Calculator
	fixtures []int // rebuilt for each test by SetUpTest
}

// Suite registers the suite with gocheck.
var _ = Suite(&CalculatorSuite{})

// SetUpSuite runs once, before any test in the suite.
func (s *CalculatorSuite) SetUpSuite(c *C) {
	c.Log("CalculatorSuite: suite fixture acquired")
}

// TearDownSuite runs once, after every test in the suite has finished.
func (s *CalculatorSuite) TearDownSuite(c *C) {
	c.Log("CalculatorSuite: suite fixture released")
}

// SetUpTest runs before each test and rebuilds the per-test fixture.
func (s *CalculatorSuite) SetUpTest(c *C) {
	s.calc = New()
	s.fixtures = []int{1, 2, 3, 4}
}

// TearDownTest runs after each test and drops the per-test fixture.
func (s *CalculatorSuite) TearDownTest(c *C) {
	s.calc = nil
	s.fixtures = nil
}

func (s *CalculatorSuite) TestAdd(c *C) {
	c.Assert(s.calc.Add(2, 3), Equals, 5)
}

func (s *CalculatorSuite) TestSub(c *C) {
	c.Assert(s.calc.Sub(10, 4), Equals, 6)
}

func (s *CalculatorSuite) TestMul(c *C) {
	c.Assert(s.calc.Mul(6, 7), Equals, 42)
}

func (s *CalculatorSuite) TestDiv(c *C) {
	got, err := s.calc.Div(9, 3)
	c.Assert(err, IsNil)
	c.Assert(got, Equals, 3)
}

func (s *CalculatorSuite) TestDivByZero(c *C) {
	_, err := s.calc.Div(1, 0)
	c.Assert(err, Equals, ErrDivideByZero)
}

// TestFixtureIsFresh proves SetUpTest rebuilt the fixture: the history starts
// empty even though earlier tests in the suite mutated a calculator.
func (s *CalculatorSuite) TestFixtureIsFresh(c *C) {
	c.Assert(s.calc.History(), HasLen, 0)
	c.Assert(s.fixtures, DeepEquals, []int{1, 2, 3, 4})

	for _, v := range s.fixtures {
		_ = s.calc.Add(v, v)
	}
	c.Assert(s.calc.History(), HasLen, len(s.fixtures))
}
