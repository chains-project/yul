'use strict';

var test = require('node:test');
var assert = require('node:assert');
var setPrototypeOf = require('../');

test('exports a function', function () {
	assert.strictEqual(typeof setPrototypeOf, 'function');
});

test('sets the prototype and returns the object', function () {
	var proto = { a: 1 };
	var obj = {};
	var result = setPrototypeOf(obj, proto);

	assert.strictEqual(result, obj);
	assert.strictEqual(Object.getPrototypeOf(obj), proto);
	assert.strictEqual(obj.a, 1);
});

test('accepts null as a prototype', function () {
	var obj = {};
	setPrototypeOf(obj, null);
	assert.strictEqual(Object.getPrototypeOf(obj), null);
});
