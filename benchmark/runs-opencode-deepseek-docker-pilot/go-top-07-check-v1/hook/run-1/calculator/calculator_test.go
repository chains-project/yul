package calculator

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Test bridges the standard `go test` entrypoint into gocheck's runner.
func Test(t *testing.T) { TestingT(t) }

// Suite registers CalculatorSuite with gocheck at package init time.
var _ = Suite(&CalculatorSuite{})

// CalculatorSuite demonstrates gocheck's suite-level and per-test fixtures.
type CalculatorSuite struct {
	calc *Calculator
}

// SetUpSuite runs once before the first test in the suite.
func (s *CalculatorSuite) SetUpSuite(c *C) {
	c.Log("suite setup")
}

// TearDownSuite runs once after the last test in the suite.
func (s *CalculatorSuite) TearDownSuite(c *C) {
	c.Log("suite teardown")
}

// SetUpTest runs before every test, giving each test a fresh Calculator.
func (s *CalculatorSuite) SetUpTest(c *C) {
	s.calc = New()
}

// TearDownTest runs after every test, even when the test panics or fails.
func (s *CalculatorSuite) TearDownTest(c *C) {
	s.calc = nil
}

func (s *CalculatorSuite) TestAdd(c *C) {
	c.Assert(s.calc.Add(2, 3), Equals, 5)
	c.Assert(s.calc.History(), DeepEquals, []string{"add"})
}

func (s *CalculatorSuite) TestDivide(c *C) {
	got, err := s.calc.Divide(10, 2)
	c.Assert(err, IsNil)
	c.Check(got, Equals, 5)
}

func (s *CalculatorSuite) TestDivideByZero(c *C) {
	_, err := s.calc.Divide(1, 0)
	c.Assert(err, ErrorMatches, "calculator: division by zero")
}

// TestFixtureIsolation relies on SetUpTest having returned a fresh instance,
// so the history written by other tests is not visible here.
func (s *CalculatorSuite) TestFixtureIsolation(c *C) {
	c.Assert(s.calc.History(), HasLen, 0)
}
