package calc

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type CalculatorSuite struct {
	calc    *Calculator
	setupID int
}

var _ = Suite(&CalculatorSuite{})

func (s *CalculatorSuite) SetUpSuite(c *C) {
	s.setupID = 1
}

func (s *CalculatorSuite) SetUpTest(c *C) {
	s.calc = New()
}

func (s *CalculatorSuite) TearDownTest(c *C) {
	s.calc = nil
}

func (s *CalculatorSuite) TearDownSuite(c *C) {
	s.setupID = 0
}

func (s *CalculatorSuite) TestAdd(c *C) {
	c.Assert(s.calc.Add(2, 3), Equals, 5)
	c.Assert(s.calc.Add(-1, 1), Equals, 0)
}

func (s *CalculatorSuite) TestSubtract(c *C) {
	c.Assert(s.calc.Subtract(10, 4), Equals, 6)
}

func (s *CalculatorSuite) TestMultiply(c *C) {
	c.Assert(s.calc.Multiply(6, 7), Equals, 42)
}

func (s *CalculatorSuite) TestDivide(c *C) {
	q, err := s.calc.Divide(10, 2)
	c.Assert(err, IsNil)
	c.Assert(q, Equals, 5)
}

func (s *CalculatorSuite) TestDivideByZero(c *C) {
	_, err := s.calc.Divide(1, 0)
	c.Assert(err, Equals, ErrDivideByZero)
}

func (s *CalculatorSuite) TestSetupRunsBeforeEachTest(c *C) {
	c.Assert(s.calc, NotNil)
	c.Assert(s.calc.History(), HasLen, 0)
}

func (s *CalculatorSuite) TestHistory(c *C) {
	s.calc.Add(1, 1)
	s.calc.Multiply(2, 2)
	c.Assert(s.calc.History(), DeepEquals, []string{"1 + 1", "2 * 2"})
}
