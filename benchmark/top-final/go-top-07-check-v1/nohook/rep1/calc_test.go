package gochecktest

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Hook up gocheck into go test.
func Test(t *testing.T) { TestingT(t) }

type CalcSuite struct {
	calc *Calc
}

var _ = Suite(&CalcSuite{})

func (s *CalcSuite) SetUpSuite(c *C) {
	c.Log("setting up CalcSuite")
}

func (s *CalcSuite) TearDownSuite(c *C) {
	c.Log("tearing down CalcSuite")
}

func (s *CalcSuite) SetUpTest(c *C) {
	s.calc = NewCalc()
}

func (s *CalcSuite) TearDownTest(c *C) {
	s.calc = nil
}

func (s *CalcSuite) TestAdd(c *C) {
	c.Assert(s.calc.Add(2), Equals, 2)
	c.Assert(s.calc.Add(3), Equals, 5)
}

func (s *CalcSuite) TestReset(c *C) {
	s.calc.Add(10)
	s.calc.Reset()
	c.Assert(s.calc.Add(1), Equals, 1)
}
