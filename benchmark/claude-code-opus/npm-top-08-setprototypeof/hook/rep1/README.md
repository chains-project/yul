# set-proto

Cross-platform helper to set the prototype of an object at runtime.

```js
const setPrototypeOf = require('set-proto');

const obj = setPrototypeOf({}, { greet() { return 'hi'; } });
obj.greet(); // 'hi'
```

Uses `Object.setPrototypeOf` when available, falling back to `__proto__`,
then to copying properties on engines that support neither. No dependencies.

## Test

```sh
npm test
```
