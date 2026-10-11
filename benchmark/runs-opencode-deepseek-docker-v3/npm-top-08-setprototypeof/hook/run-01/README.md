# proto-set

A tiny cross-platform helper for setting the prototype of an object at runtime.

It wraps [`setprototypeof`](https://www.npmjs.com/package/setprototypeof), which
uses `Object.setPrototypeOf` where available and falls back to the legacy
`__proto__` accessor elsewhere, so it works in browsers and Node.js alike.

## Install

```sh
npm install proto-set
```

## Usage

```js
import setPrototypeOf from 'proto-set'

const proto = { greet() { return 'hello' } }
const obj = {}

setPrototypeOf(obj, proto)

obj.greet() // 'hello'
```

## API

### `setPrototypeOf(obj, proto)`

Sets the prototype of `obj` to `proto` and returns `obj`.

## License

MIT
