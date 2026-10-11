'use strict';

const test = require('node:test');
const assert = require('node:assert');

const setPrototypeOf = require('../index.js');

test('sets the prototype of an object', () => {
	const proto = { greet: () => 'hi' };
	const obj = setPrototypeOf({}, proto);

	assert.strictEqual(Object.getPrototypeOf(obj), proto);
	assert.strictEqual(obj.greet(), 'hi');
});

test('returns the same object it was given', () => {
	const obj = {};
	assert.strictEqual(setPrototypeOf(obj, { a: 1 }), obj);
});

test('supports a null prototype', () => {
	const obj = setPrototypeOf({ a: 1 }, null);

	assert.strictEqual(Object.getPrototypeOf(obj), null);
	assert.strictEqual(obj.a, 1);
});

test('works through the runtime fallback', () => {
	const native = Object.setPrototypeOf;
	const modulePath = require.resolve('../index.js');

	try {
		delete Object.setPrototypeOf;
		delete require.cache[modulePath];

		const fallback = require('../index.js');
		const proto = { greet: () => 'hi' };
		const obj = fallback({}, proto);

		assert.strictEqual(Object.getPrototypeOf(obj), proto);
		assert.strictEqual(obj.greet(), 'hi');
	} finally {
		Object.setPrototypeOf = native;
		delete require.cache[modulePath];
	}
});
