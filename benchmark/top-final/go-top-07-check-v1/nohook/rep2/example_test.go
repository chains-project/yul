package gochecksuite

import (
	"testing"

	. "gopkg.in/check.v1"
)

// Hook up gocheck into go test.
func Test(t *testing.T) { TestingT(t) }

type ExampleSuite struct {
	fixture string
}

var _ = Suite(&ExampleSuite{})

func (s *ExampleSuite) SetUpSuite(c *C) {
	s.fixture = "shared-resource"
}

func (s *ExampleSuite) TearDownSuite(c *C) {
	s.fixture = ""
}

func (s *ExampleSuite) SetUpTest(c *C) {
	c.Assert(s.fixture, Equals, "shared-resource")
}

func (s *ExampleSuite) TearDownTest(c *C) {
}

func (s *ExampleSuite) TestAddition(c *C) {
	c.Assert(1+1, Equals, 2)
}

func (s *ExampleSuite) TestFixtureAvailable(c *C) {
	c.Check(s.fixture, Not(Equals), "")
}
