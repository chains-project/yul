package store

import (
	"path/filepath"
	"testing"

	. "gopkg.in/check.v1"
)

func Test(t *testing.T) { TestingT(t) }

type StoreSuite struct {
	dir   string
	store *Store
}

var _ = Suite(&StoreSuite{})

func (s *StoreSuite) SetUpSuite(c *C) {
	c.Log("starting StoreSuite")
}

func (s *StoreSuite) TearDownSuite(c *C) {
	c.Log("finished StoreSuite")
}

func (s *StoreSuite) SetUpTest(c *C) {
	s.dir = c.MkDir()
	s.store = New(filepath.Join(s.dir, "store.json"))
}

func (s *StoreSuite) TearDownTest(c *C) {
	s.store = nil
	s.dir = ""
}

func (s *StoreSuite) TestSetAndGet(c *C) {
	s.store.Set("answer", "42")

	got, err := s.store.Get("answer")
	c.Assert(err, IsNil)
	c.Check(got, Equals, "42")
	c.Check(s.store.Len(), Equals, 1)
}

func (s *StoreSuite) TestGetMissing(c *C) {
	_, err := s.store.Get("missing")
	c.Assert(err, Equals, ErrNotFound)
}

func (s *StoreSuite) TestRoundTrip(c *C) {
	s.store.Set("a", "1")
	c.Assert(s.store.Save(), IsNil)

	loaded := New(filepath.Join(s.dir, "store.json"))
	c.Assert(loaded.Load(), IsNil)

	got, err := loaded.Get("a")
	c.Assert(err, IsNil)
	c.Check(got, Equals, "1")
}
