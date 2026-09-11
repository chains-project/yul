package checksuite

import (
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type ExampleSuite struct {
	fixture string
}

var _ = Suite(&ExampleSuite{})

func (s *ExampleSuite) SetUpSuite(c *C) {
	s.fixture = "suite-wide fixture"
}

func (s *ExampleSuite) TearDownSuite(c *C) {
	s.fixture = ""
}

func (s *ExampleSuite) SetUpTest(c *C) {
	c.Log("setting up test")
}

func (s *ExampleSuite) TearDownTest(c *C) {
	c.Log("tearing down test")
}

func (s *ExampleSuite) TestFixtureIsAvailable(c *C) {
	c.Assert(s.fixture, Equals, "suite-wide fixture")
}

func (s *ExampleSuite) TestArithmetic(c *C) {
	c.Check(2+2, Equals, 4)
}
