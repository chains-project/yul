# setprototypeof

A cross-platform way to set the prototype of an object at runtime.

Works wherever JavaScript runs. It prefers the native `Object.setPrototypeOf`
when available, falls back to the `__proto__` setter on engines that support it,
and finally falls back to copying properties from the prototype for the oldest
engines.

## Install

```sh
npm install setprototypeof
```

## Usage

```js
var setPrototypeOf = require('setprototypeof')

function Animal (name) {
  this.name = name
}

Animal.prototype.speak = function () {
  return this.name + ' makes a sound.'
}

var obj = setPrototypeOf({}, Animal.prototype)

obj.name = 'Rex'
obj.speak() // => 'Rex makes a sound.'
Object.getPrototypeOf(obj) === Animal.prototype // => true
```

## API

### `setPrototypeOf(object, prototype)`

Sets the prototype of `object` to `prototype` and returns `object`.

- `object` — the object whose prototype will be changed.
- `prototype` — the new prototype, or `null`.

## License

MIT
