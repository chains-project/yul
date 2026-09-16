const setPrototypeOf = require('./index');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`✗ ${name}: ${err.message}`);
    failed++;
  }
}

function assertEqual(actual, expected, msg) {
  if (actual !== expected) {
    throw new Error(msg || `Expected ${expected}, got ${actual}`);
  }
}

function assertThrows(fn, msg) {
  try {
    fn();
    throw new Error('Expected function to throw');
  } catch (err) {
    if (err.message === 'Expected function to throw') {
      throw err;
    }
    return;
  }
}

// Test 1: Basic prototype setting
test('sets prototype using Object.setPrototypeOf', () => {
  const parent = { foo: 'bar' };
  const child = {};
  setPrototypeOf(child, parent);
  assertEqual(Object.getPrototypeOf(child), parent, 'Prototype should be set');
});

// Test 2: Setting to null
test('can set prototype to null', () => {
  const obj = Object.create({ existing: 'proto' });
  setPrototypeOf(obj, null);
  assertEqual(Object.getPrototypeOf(obj), null, 'Prototype should be null');
});

// Test 3: Chain verification
test('maintains prototype chain', () => {
  const grandparent = { a: 1 };
  const parent = { b: 2 };
  const child = {};
  setPrototypeOf(child, parent);
  setPrototypeOf(parent, grandparent);
  assertEqual(child.b, 2, 'Child should access parent property');
  assertEqual(child.a, 1, 'Child should access grandparent property');
});

// Test 4: Null input throws
test('throws when obj is null', () => {
  assertThrows(() => setPrototypeOf(null, {}), 'Should throw on null');
});

// Test 5: Undefined input throws
test('throws when obj is undefined', () => {
  assertThrows(() => setPrototypeOf(undefined, {}), 'Should throw on undefined');
});

// Test 6: Returning the same object
test('returns the modified object', () => {
  const obj = {};
  const parent = {};
  const result = setPrototypeOf(obj, parent);
  assertEqual(result, obj, 'Should return the same object');
});

// Test 7: Setting same prototype
test('can set same prototype multiple times', () => {
  const parent = { value: 42 };
  const obj = {};
  setPrototypeOf(obj, parent);
  setPrototypeOf(obj, parent);
  assertEqual(obj.value, 42, 'Property should still be accessible');
});

// Test 8: With class instances
test('works with class instances', () => {
  class Animal {
    speak() { return '...'; }
  }
  class Dog extends Animal {
    speak() { return 'woof'; }
  }
  const dog = new Dog();
  const newProto = { custom: 'method' };
  setPrototypeOf(dog, newProto);
  assertEqual(dog.custom, 'method', 'Custom method should be accessible');
  assertEqual(Object.getPrototypeOf(dog), newProto, 'Prototype should be changed');
});

// Test 9: Shim availability
test('shim function exists', () => {
  if (typeof setPrototypeOf.shim !== 'function') {
    throw new Error('shim function not exported');
  }
});

// Summary
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);