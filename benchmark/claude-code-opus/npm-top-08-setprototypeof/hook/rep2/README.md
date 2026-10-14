# set-proto

Cross-platform way to set the prototype of an object at runtime.

```js
const setPrototypeOf = require('set-proto');

const obj = setPrototypeOf({}, { greet() { return 'hi'; } });
obj.greet(); // 'hi'
```

Strategy, in order of preference:

1. Native `Object.setPrototypeOf` (ES2015+)
2. The `__proto__` setter
3. Copying the prototype's enumerable properties onto the object. This is a
   last resort for very old engines, and `Object.getPrototypeOf` will not
   reflect the change.

The individual strategies are exported as `setProtoOf` and `mixinProperties`.

## Development

```sh
npm test
```
