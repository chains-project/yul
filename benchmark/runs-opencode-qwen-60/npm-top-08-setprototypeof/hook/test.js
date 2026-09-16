"use strict"

var setPrototypeOf = require("./index")

var pass = 0
var fail = 0

function assert (label, condition) {
  if (condition) {
    pass++
  } else {
    fail++
    console.error("FAIL: " + label)
  }
}

// Test 1: Basic functionality with plain object
var obj = {}
setPrototypeOf(obj, { foo: "bar" })
assert("plain object prototype set", Object.getPrototypeOf(obj).foo === "bar")

// Test 2: null prototype
var nullProto = {}
setPrototypeOf(nullProto, null)
assert("null prototype set", Object.getPrototypeOf(nullProto) === null)

// Test 3: Custom constructor
function Animal () { this.speak = "animal" }
function Dog () { Animal.call(this) }
setPrototypeOf(Dog.prototype, Animal.prototype)
var d = new Dog()
assert("constructor prototype chain", d instanceof Animal)

// Test 4: Returns the object
var ret = {}
var result = setPrototypeOf(ret, { x: 1 })
assert("returns the object", result === ret)

// Test 5: Works with arrays
var arr = []
setPrototypeOf(arr, { custom: true })
assert("array prototype set", Object.getPrototypeOf(arr).custom === true)

console.log(pass + " passed, " + fail + " failed")
if (fail > 0) process.exit(1)