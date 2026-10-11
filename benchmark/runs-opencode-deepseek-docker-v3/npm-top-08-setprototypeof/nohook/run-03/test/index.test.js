'use strict';

var test = require('node:test');
var assert = require('node:assert');

var setPrototypeOf = require('../');

test('sets the prototype of an object', function () {
	var proto = { greet: function () { return 'hello'; } };
	var obj = {};

	assert.strictEqual(setPrototypeOf(obj, proto), obj);
	assert.strictEqual(Object.getPrototypeOf(obj), proto);
	assert.strictEqual(obj.greet(), 'hello');
});

test('sets the prototype to null', function () {
	var obj = {};

	setPrototypeOf(obj, null);

	assert.strictEqual(Object.getPrototypeOf(obj), null);
});

test('changes instanceof behavior', function () {
	function Animal() {}
	function Dog() {}

	var dog = new Animal();
	setPrototypeOf(dog, Dog.prototype);

	assert.ok(dog instanceof Dog);
	assert.ok(!(dog instanceof Animal));
});

test('createSetPrototypeOf prefers the native implementation', function () {
	assert.strictEqual(setPrototypeOf.createSetPrototypeOf(), Object.setPrototypeOf);
});

test('setProtoOf fallback uses the __proto__ setter', function () {
	var proto = { a: 1 };
	var obj = {};

	assert.strictEqual(setPrototypeOf.setProtoOf(obj, proto), obj);
	assert.strictEqual(Object.getPrototypeOf(obj), proto);
});

test('mixinProperties fallback copies inherited enumerable props', function () {
	var proto = { a: 1, b: 2 };
	var obj = { b: 'own', c: 3 };

	assert.strictEqual(setPrototypeOf.mixinProperties(obj, proto), obj);
	assert.strictEqual(obj.a, 1);
	assert.strictEqual(obj.b, 'own');
	assert.strictEqual(obj.c, 3);
});

test('mixinProperties copies enumerable props from the whole chain', function () {
	var base = { inherited: true };
	var proto = Object.create(base);
	proto.own = 'yes';

	var obj = {};
	setPrototypeOf.mixinProperties(obj, proto);

	assert.strictEqual(obj.own, 'yes');
	assert.strictEqual(obj.inherited, true);
});
