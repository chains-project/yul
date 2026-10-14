# set-proto

Cross-platform helper to set an object's prototype at runtime.

```js
const setPrototypeOf = require('set-proto');

const obj = setPrototypeOf({}, Foo.prototype);
obj instanceof Foo; // true
```

Uses native `Object.setPrototypeOf` when available, falling back to the
`__proto__` setter, and finally to copying properties on very old engines.

## Development

```sh
npm test
```
