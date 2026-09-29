# setprototypeof

A small, dependency-free, cross-platform helper to set the prototype
(i.e. the internal `[[Prototype]]`) of an object at runtime.

It picks the best mechanism the current runtime offers:

1. `Object.setPrototypeOf` (ES2015)
2. the `__proto__` accessor (widely implemented, including old browsers)
3. a property-copying fallback for engines that support neither

## Install

```sh
npm install setprototypeof
```

## Usage

```js
const setPrototypeOf = require('setprototypeof');

const proto = { greet() { return 'hi'; } };
const obj = setPrototypeOf({}, proto);

obj.greet();                        // 'hi'
Object.getPrototypeOf(obj) === proto; // true
```

The function returns the same object it was given, so it can be composed.
Passing `null` creates an object with no prototype:

```js
const bare = setPrototypeOf({}, null);
Object.getPrototypeOf(bare); // null
```

## API

### `setPrototypeOf(obj, proto)`

| Param   | Type             | Description                              |
| ------- | ---------------- | ---------------------------------------- |
| `obj`   | `Object`         | The object whose prototype will be set.  |
| `proto` | `Object \| null` | The new prototype.                       |

Returns `obj`.

## Notes

The final fallback cannot truly retarget a prototype chain on engines that
lack both `Object.setPrototypeOf` and `__proto__`. In that case the helper
copies the enumerable inherited members onto the target so code that only
relies on inherited properties still works.

## License

MIT
