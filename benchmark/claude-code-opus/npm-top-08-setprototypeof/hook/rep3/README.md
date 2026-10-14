# cross-setprototypeof

Cross-platform way to set the prototype of an object at runtime.

```js
const setPrototypeOf = require('cross-setprototypeof')

const obj = setPrototypeOf({}, { greet () { return 'hi' } })
obj.greet() // 'hi'
```

Strategy, in order of preference:

1. Native `Object.setPrototypeOf`
2. The `__proto__` accessor
3. Copying the prototype's enumerable properties onto the object (no real
   prototype link, so `instanceof` and later prototype changes won't apply)

## Development

```sh
npm test
```
