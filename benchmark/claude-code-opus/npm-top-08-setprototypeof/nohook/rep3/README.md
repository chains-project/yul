# set-proto

Cross-platform way to set the prototype of an object at runtime.

```js
const setPrototypeOf = require('set-proto');

const obj = setPrototypeOf({}, { greet() { return 'hi'; } });
obj.greet(); // 'hi'
```

Uses the native `Object.setPrototypeOf` when available, falling back to the
`__proto__` setter and finally to copying properties on legacy engines.

## Development

```sh
npm test
```
