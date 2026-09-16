package hook

import (
	"testing"

	. "gopkg.in/check.v1"
)

// SuiteHook is the main test suite struct
type SuiteHook struct {
	store   *Store
	key1    string
	value1  string
	key2    string
	value2  string
	cleanup []string
}

var _ = Suite(&SuiteHook{})

// SetUpSuite runs once before all tests in the suite
func (s *SuiteHook) SetUpSuite(c *C) {
	c.Log("Setting up suite fixtures...")
}

// TearDownSuite runs once after all tests in the suite
func (s *SuiteHook) TearDownSuite(c *C) {
	c.Log("Tearing down suite fixtures...")
}

// SetUpTest runs before each test method
func (s *SuiteHook) SetUpTest(c *C) {
	c.Log("Setting up test: " + c.TestName())
	s.store = NewStore()
	s.key1 = "name"
	s.value1 = "alice"
	s.key2 = "email"
	s.value2 = "alice@example.com"
	s.cleanup = []string{}
}

// TearDownTest runs after each test method
func (s *SuiteHook) TearDownTest(c *C) {
	c.Log("Tearing down test: " + c.TestName())
	s.store = nil
	s.key1 = ""
	s.value1 = ""
	s.key2 = ""
	s.value2 = ""
	s.cleanup = append(s.cleanup, "final cleanup")
}

// TestStoreCreation tests that a new store is created correctly
func (s *SuiteHook) TestStoreCreation(c *C) {
	store := NewStore()
	c.Assert(store, NotNil)
	c.Assert(store.Len(), Equals, 0)
	c.Assert(store.data, NotNil)
}

// TestStoreSetGet tests basic set and get operations
func (s *SuiteHook) TestStoreSetGet(c *C) {
	s.store.Set(s.key1, s.value1)
	val, err := s.store.Get(s.key1)
	c.Assert(err, IsNil)
	c.Assert(val, Equals, s.value1)
	c.Assert(s.store.Len(), Equals, 1)
}

// TestStoreGetNotFound tests behavior when key doesn't exist
func (s *SuiteHook) TestStoreGetNotFound(c *C) {
	_, err := s.store.Get("nonexistent")
	c.Assert(err, Equals, ErrNotFound)
	c.Assert(s.store.Len(), Equals, 0)
}

// TestStoreHas tests the Has method
func (s *SuiteHook) TestStoreHas(c *C) {
	s.store.Set(s.key1, s.value1)
	c.Assert(s.store.Has(s.key1), Equals, true)
	c.Assert(s.store.Has("missing"), Equals, false)
}

// TestStoreDelete tests deletion
func (s *SuiteHook) TestStoreDelete(c *C) {
	s.store.Set(s.key1, s.value1)
	s.store.Set(s.key2, s.value2)
	c.Assert(s.store.Len(), Equals, 2)
	s.store.Delete(s.key1)
	c.Assert(s.store.Len(), Equals, 1)
	c.Assert(s.store.Has(s.key1), Equals, false)
	c.Assert(s.store.Has(s.key2), Equals, true)
}

// TestStoreOverwrite tests overwriting an existing key
func (s *SuiteHook) TestStoreOverwrite(c *C) {
	s.store.Set(s.key1, s.value1)
	s.store.Set(s.key1, "bob")
	val, err := s.store.Get(s.key1)
	c.Assert(err, IsNil)
	c.Assert(val, Equals, "bob")
	c.Assert(s.store.Len(), Equals, 1)
}

// TestStoreMultipleOperations tests multiple operations in sequence
func (s *SuiteHook) TestStoreMultipleOperations(c *C) {
	for i := 0; i < 10; i++ {
		key := "key" + string(rune('0'+i))
		val := "value" + string(rune('0'+i))
		s.store.Set(key, val)
	}
	c.Assert(s.store.Len(), Equals, 10)
	for i := 0; i < 10; i++ {
		key := "key" + string(rune('0'+i))
		expected := "value" + string(rune('0'+i))
		v, err := s.store.Get(key)
		c.Assert(err, IsNil)
		c.Assert(v, Equals, expected)
	}
}

// TestSuiteMain runs the gocheck test suite from standard go test
func TestSuiteMain(t *testing.T) {
	TestingT(t)
}