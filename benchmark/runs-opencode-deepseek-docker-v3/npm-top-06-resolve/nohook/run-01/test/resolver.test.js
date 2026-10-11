import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { after, before, describe, it } from 'node:test';

import { ModuleNotFoundError, Resolver, resolve } from '../src/index.js';

let root;
let src;

function write(relativePath, contents = '') {
  const target = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, contents);
  return target;
}

before(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'module-resolver-'));
  src = path.join(root, 'src');

  write('src/index.js');
  write('src/util.js');
  write('src/lib/index.js');
  write('src/pkg/package.json', JSON.stringify({ name: 'pkg', main: 'lib/main.js' }));
  write('src/pkg/lib/main.js');
  write('node_modules/left-pad/package.json', JSON.stringify({ name: 'left-pad', main: 'index.js' }));
  write('node_modules/left-pad/index.js');
  write('node_modules/nested/package.json', JSON.stringify({ name: 'nested', main: './src/entry' }));
  write('node_modules/nested/src/entry.js');
  write('node_modules/nested/src/other.json', '{}');
});

after(() => {
  fs.rmSync(root, { recursive: true, force: true });
});

describe('core modules', () => {
  it('resolves builtin names', () => {
    assert.equal(resolve('fs'), 'fs');
  });

  it('resolves node: prefixed builtins', () => {
    assert.equal(resolve('node:fs'), 'node:fs');
  });
});

describe('relative and absolute paths', () => {
  it('resolves an exact file', () => {
    assert.equal(resolve('./util.js', { basedir: src }), path.join(src, 'util.js'));
  });

  it('appends a known extension', () => {
    assert.equal(resolve('./util', { basedir: src }), path.join(src, 'util.js'));
  });

  it('resolves a directory index', () => {
    assert.equal(resolve('./lib', { basedir: src }), path.join(src, 'lib', 'index.js'));
  });

  it('resolves an absolute path', () => {
    assert.equal(resolve(path.join(src, 'util')), path.join(src, 'util.js'));
  });

  it('accepts a file path via the from option', () => {
    const from = path.join(src, 'index.js');
    assert.equal(resolve('./util', { from }), path.join(src, 'util.js'));
  });
});

describe('package directories', () => {
  it('honours the package.json main field', () => {
    assert.equal(resolve('./pkg', { basedir: src }), path.join(src, 'pkg', 'lib', 'main.js'));
  });

  it('resolves a main entry without an extension', () => {
    assert.equal(
      resolve('nested', { basedir: src }),
      path.join(root, 'node_modules', 'nested', 'src', 'entry.js'),
    );
  });
});

describe('node_modules resolution', () => {
  it('finds a bare specifier', () => {
    assert.equal(
      resolve('left-pad', { basedir: src }),
      path.join(root, 'node_modules', 'left-pad', 'index.js'),
    );
  });

  it('resolves a subpath within a package', () => {
    assert.equal(
      resolve('nested/src/other.json', { basedir: src }),
      path.join(root, 'node_modules', 'nested', 'src', 'other.json'),
    );
  });
});

describe('errors', () => {
  it('throws MODULE_NOT_FOUND for missing modules', () => {
    assert.throws(
      () => resolve('./missing', { basedir: src }),
      (error) => error instanceof ModuleNotFoundError && error.code === 'MODULE_NOT_FOUND',
    );
  });

  it('rejects empty requests', () => {
    assert.throws(() => resolve(''), TypeError);
  });
});

describe('Resolver class', () => {
  it('uses basedir for every request', () => {
    const resolver = new Resolver({ basedir: src });
    assert.equal(resolver.resolve('./util'), path.join(src, 'util.js'));
  });
});
