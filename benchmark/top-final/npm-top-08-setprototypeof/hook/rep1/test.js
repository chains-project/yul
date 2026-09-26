'use strict'

const assert = require('assert')
const setPrototypeOf = require('./index')

function Base () {}
Base.prototype.hello = function () { return 'hi' }

const obj = {}
setPrototypeOf(obj, Base.prototype)

assert.strictEqual(obj.hello(), 'hi')
console.log('ok')
