const assert = require('assert');
const { resolveModule } = require('./index');

const selfPath = resolveModule('resolve', __dirname);
assert.ok(selfPath.endsWith('.js'), `expected a .js file, got ${selfPath}`);

const relativePath = resolveModule('./index', __dirname);
assert.strictEqual(relativePath, require.resolve('./index'));

assert.throws(() => resolveModule('this-package-does-not-exist', __dirname));

console.log('all tests passed');
