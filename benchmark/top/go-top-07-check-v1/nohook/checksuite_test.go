package checksuite

import (
	"testing"

	check "gopkg.in/check.v1"
)

func Test(t *testing.T) { check.TestingT(t) }

type ExampleSuite struct {
	fixture string
}

var _ = check.Suite(&ExampleSuite{})

func (s *ExampleSuite) SetUpSuite(c *check.C) {
	s.fixture = "suite-fixture"
}

func (s *ExampleSuite) TearDownSuite(c *check.C) {
	s.fixture = ""
}

func (s *ExampleSuite) SetUpTest(c *check.C) {
	c.Assert(s.fixture, check.Equals, "suite-fixture")
}

func (s *ExampleSuite) TearDownTest(c *check.C) {}

func (s *ExampleSuite) TestExample(c *check.C) {
	c.Check(1+1, check.Equals, 2)
}
