package calc

import (
	"testing"

	"github.com/stretchr/testify/suite"
)

type CalculatorSuite struct {
	suite.Suite

	calc *Calculator
	env  string
}

func (s *CalculatorSuite) SetupSuite() {
	s.env = "suite-fixture"
}

func (s *CalculatorSuite) TearDownSuite() {
	s.env = ""
}

func (s *CalculatorSuite) SetupTest() {
	s.calc = &Calculator{}
}

func (s *CalculatorSuite) TearDownTest() {
	s.calc = nil
}

func (s *CalculatorSuite) BeforeTest(suiteName, testName string) {
	s.T().Logf("running %s.%s with env=%s", suiteName, testName, s.env)
}

func (s *CalculatorSuite) TestAdd() {
	s.Equal(4, s.calc.Add(2, 2))
	s.Len(s.calc.History(), 1)
}

func (s *CalculatorSuite) TestDivide() {
	got, err := s.calc.Divide(10, 2)
	s.Require().NoError(err)
	s.Equal(5, got)
}

func (s *CalculatorSuite) TestDivideByZero() {
	_, err := s.calc.Divide(1, 0)
	s.Require().ErrorIs(err, ErrDivideByZero)
}

func TestCalculatorSuite(t *testing.T) {
	suite.Run(t, new(CalculatorSuite))
}
