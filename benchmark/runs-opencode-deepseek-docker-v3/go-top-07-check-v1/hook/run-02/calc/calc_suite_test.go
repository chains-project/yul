package calc_test

import (
	"testing"

	"example.com/testkit/calc"

	"github.com/stretchr/testify/suite"
)

type CalculatorSuite struct {
	suite.Suite
	calculator *calc.Calculator
}

func (s *CalculatorSuite) SetupSuite() {
	s.T().Log("setting up suite (runs once before all tests)")
}

func (s *CalculatorSuite) TearDownSuite() {
	s.T().Log("tearing down suite (runs once after all tests)")
}

func (s *CalculatorSuite) SetupTest() {
	s.calculator = &calc.Calculator{}
}

func (s *CalculatorSuite) TearDownTest() {
	s.calculator = nil
}

func (s *CalculatorSuite) BeforeTest(suiteName, testName string) {
	s.T().Logf("before %s.%s", suiteName, testName)
}

func (s *CalculatorSuite) AfterTest(suiteName, testName string) {
	s.T().Logf("after %s.%s", suiteName, testName)
}

func (s *CalculatorSuite) TestAdd() {
	s.Equal(5, s.calculator.Add(2, 3))
	s.Equal(5, s.calculator.Add(3, 2), "addition should be commutative")
}

func (s *CalculatorSuite) TestDivide() {
	result, err := s.calculator.Divide(10, 2)
	s.Require().NoError(err)
	s.Equal(5, result)
}

func (s *CalculatorSuite) TestDivideByZero() {
	_, err := s.calculator.Divide(1, 0)
	s.Error(err)
}

func (s *CalculatorSuite) TestHistoryFixtureIsolation() {
	s.Empty(s.calculator.History())
	s.calculator.Add(1, 1)
	s.Len(s.calculator.History(), 1)
}

func TestCalculatorSuite(t *testing.T) {
	suite.Run(t, new(CalculatorSuite))
}
