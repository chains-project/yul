'use strict';

var test = require('node:test');
var assert = require('node:assert');

function loadPolyfill() {
	delete require.cache[require.resolve('../index')];
	delete require.cache[require.resolve('../polyfill')];
	return require('../polyfill');
}

test('polyfill installs Object.setPrototypeOf', function () {
	var original = Object.setPrototypeOf;
	delete Object.setPrototypeOf;

	try {
		loadPolyfill();
		assert.strictEqual(typeof Object.setPrototypeOf, 'function');

		var proto = { x: 1 };
		var obj = {};
		Object.setPrototypeOf(obj, proto);
		assert.strictEqual(Object.getPrototypeOf(obj), proto);
	} finally {
		Object.setPrototypeOf = original;
	}
});

test('polyfill installs Reflect.setPrototypeOf', function () {
	var original = Reflect.setPrototypeOf;
	delete Reflect.setPrototypeOf;

	try {
		loadPolyfill();
		assert.strictEqual(typeof Reflect.setPrototypeOf, 'function');

		var proto = { y: 1 };
		var obj = {};
		assert.strictEqual(Reflect.setPrototypeOf(obj, proto), true);
		assert.strictEqual(Object.getPrototypeOf(obj), proto);
	} finally {
		Reflect.setPrototypeOf = original;
	}
});

test('Reflect.setPrototypeOf polyfill rejects non-objects', function () {
	var original = Reflect.setPrototypeOf;
	delete Reflect.setPrototypeOf;

	try {
		loadPolyfill();
		assert.throws(function () {
			Reflect.setPrototypeOf(1, {});
		}, TypeError);
	} finally {
		Reflect.setPrototypeOf = original;
	}
});
