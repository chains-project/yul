package calculator

import (
	"errors"
	"testing"

	. "gopkg.in/check.v1"
)

func TestCalculator(t *testing.T) {
	TestingT(t)
}

type CalculatorSuite struct {
	calc *Calculator
}

var _ = Suite(&CalculatorSuite{})

func (s *CalculatorSuite) SetUpSuite(c *C) {
	c.Log("starting CalculatorSuite")
}

func (s *CalculatorSuite) TearDownSuite(c *C) {
	c.Log("finished CalculatorSuite")
}

func (s *CalculatorSuite) SetUpTest(c *C) {
	s.calc = New()
	c.Assert(s.calc.History(), HasLen, 0)
}

func (s *CalculatorSuite) TearDownTest(c *C) {
	s.calc.Reset()
	c.Assert(s.calc.History(), HasLen, 0)
}

func (s *CalculatorSuite) TestAdd(c *C) {
	c.Assert(s.calc.Add(2, 3), Equals, 5)
	c.Assert(s.calc.Add(-1, 1), Equals, 0)
}

func (s *CalculatorSuite) TestAddRecordsHistory(c *C) {
	s.calc.Add(1, 2)
	s.calc.Add(3, 4)
	c.Assert(s.calc.History(), DeepEquals, []int{3, 7})
}

func (s *CalculatorSuite) TestDivide(c *C) {
	got, err := s.calc.Divide(10, 2)
	c.Assert(err, IsNil)
	c.Assert(got, Equals, 5)
}

func (s *CalculatorSuite) TestDivideByZero(c *C) {
	_, err := s.calc.Divide(1, 0)
	c.Assert(err, ErrorMatches, "division by zero")
	c.Assert(err, ErrorCheckerInst, ErrDivideByZero)
}

func (s *CalculatorSuite) TestFixturesAreIsolated(c *C) {
	c.Assert(s.calc.History(), HasLen, 0, Commentf("SetUpTest should provide a fresh fixture"))
}

type ErrorChecker struct{}

var ErrorCheckerInst = &ErrorChecker{}

func (checker *ErrorChecker) Info() *CheckerInfo {
	return &CheckerInfo{Name: "ErrorChecker", Params: []string{"obtained", "expected"}}
}

func (checker *ErrorChecker) Check(params []interface{}, names []string) (bool, string) {
	err, ok := params[0].(error)
	if !ok {
		return false, "obtained value is not an error"
	}
	target, ok := params[1].(error)
	if !ok {
		return false, "expected value is not an error"
	}
	if errors.Is(err, target) {
		return true, ""
	}
	return false, ""
}
