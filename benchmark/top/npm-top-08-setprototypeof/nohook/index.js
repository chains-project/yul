const setPrototypeOf = require('setprototypeof');

function CustomError(message) {
  this.message = message;
}

setPrototypeOf(CustomError.prototype, Error.prototype);

module.exports = CustomError;
