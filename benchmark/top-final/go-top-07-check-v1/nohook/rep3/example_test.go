package gochecksuite

import (
	"testing"

	check "gopkg.in/check.v1"
)

func Test(t *testing.T) { check.TestingT(t) }

type ExampleSuite struct {
	fixture int
}

var _ = check.Suite(&ExampleSuite{})

func (s *ExampleSuite) SetUpSuite(c *check.C) {
	s.fixture = 1
}

func (s *ExampleSuite) TearDownSuite(c *check.C) {}

func (s *ExampleSuite) SetUpTest(c *check.C) {
	s.fixture++
}

func (s *ExampleSuite) TearDownTest(c *check.C) {}

func (s *ExampleSuite) TestFixtureIncremented(c *check.C) {
	c.Assert(s.fixture, check.Equals, 2)
}
