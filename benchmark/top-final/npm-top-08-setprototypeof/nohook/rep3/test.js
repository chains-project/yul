const assert = require('assert');
const setPrototypeOf = require('./index.js');

function Animal() {}
const obj = {};
setPrototypeOf(obj, Animal.prototype);

assert.strictEqual(Object.getPrototypeOf(obj), Animal.prototype);
console.log('ok');
