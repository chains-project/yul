package store_test

import (
	"os"
	"path/filepath"
	"testing"

	. "gopkg.in/check.v1"

	"example.com/project/store"
)

// Test hooks gocheck into the standard "go test" runner.
// One such function per package is enough to run every registered suite.
func Test(t *testing.T) { TestingT(t) }

type StoreSuite struct {
	dir   string       // suite-wide fixture, created once
	store *store.Store // per-test fixture, recreated for every test
}

var _ = Suite(&StoreSuite{})

// SetUpSuite runs once before any test in the suite.
func (s *StoreSuite) SetUpSuite(c *C) {
	// c.MkDir returns a temp directory removed automatically after the suite.
	s.dir = c.MkDir()
}

// TearDownSuite runs once after all tests in the suite.
func (s *StoreSuite) TearDownSuite(c *C) {}

// SetUpTest runs before each test, giving every test a fresh store.
func (s *StoreSuite) SetUpTest(c *C) {
	s.store = store.New()
	s.store.Set("seed", "value")
}

// TearDownTest runs after each test, even if it failed.
func (s *StoreSuite) TearDownTest(c *C) {
	s.store = nil
}

func (s *StoreSuite) TestGetSeeded(c *C) {
	v, err := s.store.Get("seed")
	c.Assert(err, IsNil)
	c.Check(v, Equals, "value")
}

func (s *StoreSuite) TestSetOverwrites(c *C) {
	s.store.Set("seed", "new")
	v, err := s.store.Get("seed")
	c.Assert(err, IsNil)
	c.Check(v, Equals, "new")
	c.Check(s.store.Len(), Equals, 1)
}

func (s *StoreSuite) TestGetMissing(c *C) {
	_, err := s.store.Get("nope")
	c.Check(err, Equals, store.ErrNotFound)
	c.Check(err, ErrorMatches, ".*not found")
}

func (s *StoreSuite) TestSuiteDirFixture(c *C) {
	path := filepath.Join(s.dir, "snapshot")
	c.Assert(os.WriteFile(path, []byte("ok"), 0o644), IsNil)
	data, err := os.ReadFile(path)
	c.Assert(err, IsNil)
	c.Check(string(data), DeepEquals, "ok")
}

// Benchmarks run with: go test ./... -check.b
func (s *StoreSuite) BenchmarkSet(c *C) {
	for i := 0; i < c.N; i++ {
		s.store.Set("k", "v")
	}
}
