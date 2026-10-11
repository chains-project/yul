'use strict'

var setPrototypeOf = require('setprototypeof')

module.exports = function setPrototype(target, prototype) {
  return setPrototypeOf(target, prototype)
}
