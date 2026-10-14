# set-proto

Set the prototype of an object at runtime.

```js
const setPrototypeOf = require('set-proto');

const obj = setPrototypeOf({}, { greet() { return 'hi'; } });
obj.greet(); // 'hi'
```

Built on the standard `Object.setPrototypeOf`, so it has no dependencies and
works on all supported Node.js versions and modern browsers.

## Development

```sh
npm test
```
