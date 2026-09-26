const setPrototypeOf = require('setprototypeof');

function CustomError(message) {
  this.message = message;
  setPrototypeOf(this, CustomError.prototype);
}
setPrototypeOf(CustomError.prototype, Error.prototype);

const err = new CustomError('something broke');
console.log(err instanceof CustomError, err instanceof Error, err.message);
