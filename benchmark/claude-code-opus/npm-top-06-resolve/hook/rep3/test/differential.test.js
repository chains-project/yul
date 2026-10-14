import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import path from 'node:path';
import { after, before, describe, test } from 'node:test';
import { Resolver } from '../src/index.js';
import { createFixture } from './fixtures.js';

/**
 * Every case is resolved by both Node's real `require.resolve` and our
 * Resolver; the results (path, or error code) must be identical.
 */
const cases = {
  'src/app.js': [
    './data', './data.json', './native', './only-file', './only-file/', './both', './both/',
    './dir', './dir/', './dir/.', './dir-with-main', './main-dir', './bad-main', './broken-main',
    './bad-json', './missing', '../main', '..', '.', '../src/./app',
    'fs', 'node:fs', 'fs/promises', 'node:test', 'test',
    'plain', 'plain/index', 'plain/', 'main-pkg', 'main-pkg/other', 'main-pkg/lib/m.js',
    'exp-pkg', 'exp-pkg/sub/a', 'exp-pkg/sub/private/x', 'exp-pkg/notexported.js',
    'exp-pkg/data.json', 'exp-pkg/pkg', 'exp-pkg/bad', 'exp-pkg/dotdot', 'exp-pkg/arr',
    'exp-pkg/missing', 'exp-pkg/package.json', 'exp-pkg/dir/a.js',
    'sugar', 'sugar/s.js', 'conds',
    '@scope/pkg/x', '@scope/pkg', '@scope/legacy', '@scope',
    'linked', 'mixed',
    'pattern/foo', 'pattern/foo.js', 'pattern/features/x', 'pattern/features/internal/y',
    'pattern/node_modules/x', 'pattern/a/../foo',
    'project', 'project/feature', 'project/nope', 'project/main.js',
    '#internal/a', '#internal/missing', '#dep', '#dep-sub/a', '#cond', '#escape', '#nope', '#', '#/x',
    'missing-pkg', 'missing-pkg/sub',
  ],
  'nested/deep/file.js': ['plain', 'exp-pkg', 'project', '#cond', '../../main'],
  'node_modules/exp-pkg/cjs.js': ['exp-pkg', 'exp-pkg/sub/a', '#self-internal', 'project', '#cond', 'plain'],
  'src/': ['./data', 'plain', '#cond'],
};

function outcome(fn) {
  try {
    return { path: fn() };
  } catch (err) {
    return { code: err.code ?? err.name };
  }
}

describe('matches require.resolve', () => {
  let fixture;
  before(() => {
    fixture = createFixture();
  });
  after(() => fixture.cleanup());

  for (const [from, requests] of Object.entries(cases)) {
    describe(`from ${from}`, () => {
      for (const request of requests) {
        test(JSON.stringify(request), () => {
          const parentPath = path.join(fixture.projectDir, from) + (from.endsWith('/') ? '/' : '');
          const expected = outcome(() => createRequire(parentPath).resolve(request));
          const actual = outcome(() => new Resolver().resolve(request, parentPath));
          assert.deepEqual(actual, expected);
        });
      }
    });
  }

  test('absolute request', () => {
    const parentPath = path.join(fixture.projectDir, 'src/app.js');
    for (const request of [path.join(fixture.projectDir, 'main'), path.join(fixture.projectDir, 'src/dir/')]) {
      assert.deepEqual(
        outcome(() => new Resolver().resolve(request, parentPath)),
        outcome(() => createRequire(parentPath).resolve(request)),
      );
    }
  });

  test('preserveSymlinks keeps the symlinked path', () => {
    const parentPath = path.join(fixture.projectDir, 'src/app.js');
    assert.equal(
      new Resolver({ preserveSymlinks: true }).resolve('linked', parentPath),
      path.join(fixture.projectDir, 'node_modules/linked/index.js'),
    );
  });

  test('custom conditions select different exports', () => {
    const parentPath = path.join(fixture.projectDir, 'src/app.js');
    const resolver = new Resolver({ conditions: ['import'] });
    assert.equal(resolver.resolve('exp-pkg', parentPath), path.join(fixture.projectDir, 'node_modules/exp-pkg/esm.mjs'));
  });

  test('custom extensions', () => {
    const parentPath = path.join(fixture.projectDir, 'src/app.js');
    assert.throws(() => new Resolver({ extensions: ['.json'] }).resolve('./both', parentPath), {
      code: 'MODULE_NOT_FOUND',
    });
    assert.equal(
      new Resolver({ extensions: ['.json'] }).resolve('./data', parentPath),
      path.join(fixture.projectDir, 'src/data.json'),
    );
  });
});
