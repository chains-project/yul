# expand-range

Expand a range like `1-10` or `a-z` into an array of every value in between.

```js
import { expandRange } from './src/expandRange.js';

expandRange('1-5');  // [1, 2, 3, 4, 5]
expandRange('5-1');  // [5, 4, 3, 2, 1]
expandRange('-2-2'); // [-2, -1, 0, 1, 2]
expandRange('a-e');  // ['a', 'b', 'c', 'd', 'e']
```

CLI:

```sh
npm start -- 1-10 a-z
```

Tests: `npm test` (uses the built-in `node:test` runner, no dependencies).
