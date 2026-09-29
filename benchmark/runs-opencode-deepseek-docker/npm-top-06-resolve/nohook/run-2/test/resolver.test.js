import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import {
  Resolver,
  resolveSync,
  PackagePathNotExportedError,
  PackageImportNotDefinedError,
} from '../src/index.js';

function writeTree(root, tree) {
  for (const [relative, contents] of Object.entries(tree)) {
    const full = path.join(root, relative);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    const body =
      typeof contents === 'string'
        ? contents
        : `${JSON.stringify(contents, null, 2)}\n`;
    fs.writeFileSync(full, body);
  }
}

function makeProject(tree) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'nmr-')));
  writeTree(root, tree);
  return root;
}

test('returns core module specifiers unchanged', () => {
  assert.equal(resolveSync('fs'), 'fs');
  assert.equal(resolveSync('node:path'), 'node:path');
});

test('resolves relative files, extensions, and directories', () => {
  const root = makeProject({
    'src/a.js': '',
    'src/b/index.js': '',
    'src/c/package.json': { main: 'lib/entry.js' },
    'src/c/lib/entry.js': '',
    'src/d/package.json': { main: '.' },
    'src/d/index.json': '{}',
  });
  const basedir = path.join(root, 'src');

  assert.equal(resolveSync('./a', { basedir }), path.join(root, 'src/a.js'));
  assert.equal(resolveSync('./a.js', { basedir }), path.join(root, 'src/a.js'));
  assert.equal(resolveSync('./b', { basedir }), path.join(root, 'src/b/index.js'));
  assert.equal(resolveSync('./c', { basedir }), path.join(root, 'src/c/lib/entry.js'));
  assert.equal(resolveSync('./d', { basedir }), path.join(root, 'src/d/index.json'));
  assert.equal(
    resolveSync(path.join(root, 'src/a.js'), { basedir }),
    path.join(root, 'src/a.js'),
  );
});

test('walks node_modules, including nested packages and scopes', () => {
  const root = makeProject({
    'app/index.js': '',
    'app/node_modules/left-pad/package.json': { main: 'index.js' },
    'app/node_modules/left-pad/index.js': '',
    'app/node_modules/left-pad/extra.js': '',
    'app/node_modules/bare/index.js': '',
    'app/node_modules/@scope/pkg/package.json': { main: 'main.js' },
    'app/node_modules/@scope/pkg/main.js': '',
    'app/packages/inner/index.js': '',
    'app/packages/inner/node_modules/left-pad/package.json': { main: 'inner.js' },
    'app/packages/inner/node_modules/left-pad/inner.js': '',
  });
  const app = path.join(root, 'app');

  assert.equal(resolveSync('left-pad', { basedir: app }), path.join(app, 'node_modules/left-pad/index.js'));
  assert.equal(resolveSync('left-pad/extra', { basedir: app }), path.join(app, 'node_modules/left-pad/extra.js'));
  assert.equal(resolveSync('bare', { basedir: app }), path.join(app, 'node_modules/bare/index.js'));
  assert.equal(resolveSync('@scope/pkg', { basedir: app }), path.join(app, 'node_modules/@scope/pkg/main.js'));

  const inner = path.join(app, 'packages/inner');
  assert.equal(resolveSync('left-pad', { basedir: inner }), path.join(inner, 'node_modules/left-pad/inner.js'));
  assert.equal(resolveSync('@scope/pkg', { basedir: inner }), path.join(app, 'node_modules/@scope/pkg/main.js'));
});

test('honors the exports field, conditions, subpaths, and patterns', () => {
  const root = makeProject({
    'app/node_modules/pkg/package.json': {
      exports: {
        '.': { require: './cjs.js', import: './esm.mjs' },
        './feature': './feature.js',
        './pattern/*': './lib/*.js',
      },
      main: './legacy.js',
    },
    'app/node_modules/pkg/cjs.js': '',
    'app/node_modules/pkg/esm.mjs': '',
    'app/node_modules/pkg/feature.js': '',
    'app/node_modules/pkg/lib/x.js': '',
    'app/node_modules/pkg/legacy.js': '',
    'app/node_modules/pkg/secret.js': '',
  });
  const app = path.join(root, 'app');
  const pkg = path.join(app, 'node_modules/pkg');

  assert.equal(resolveSync('pkg', { basedir: app }), path.join(pkg, 'cjs.js'));
  assert.equal(
    resolveSync('pkg', { basedir: app, conditions: ['node', 'import'] }),
    path.join(pkg, 'esm.mjs'),
  );
  assert.equal(resolveSync('pkg/feature', { basedir: app }), path.join(pkg, 'feature.js'));
  assert.equal(resolveSync('pkg/pattern/x', { basedir: app }), path.join(pkg, 'lib/x.js'));

  assert.throws(
    () => resolveSync('pkg/secret', { basedir: app }),
    (error) => error instanceof PackagePathNotExportedError && error.code === 'ERR_PACKAGE_PATH_NOT_EXPORTED',
  );
});

test('resolves package imports (#specifiers) relative to the package scope', () => {
  const root = makeProject({
    'app/package.json': {
      imports: {
        '#dep': './src/dep.js',
        '#cond': { require: './src/cjs.js', default: './src/default.js' },
      },
    },
    'app/src/dep.js': '',
    'app/src/cjs.js': '',
    'app/src/default.js': '',
    'app/src/consumer.js': '',
  });
  const basedir = path.join(root, 'app/src');

  assert.equal(resolveSync('#dep', { basedir }), path.join(root, 'app/src/dep.js'));
  assert.equal(resolveSync('#cond', { basedir }), path.join(root, 'app/src/cjs.js'));
  assert.equal(
    resolveSync('#cond', { basedir, conditions: ['import'] }),
    path.join(root, 'app/src/default.js'),
  );
  assert.throws(
    () => resolveSync('#missing', { basedir }),
    (error) => error instanceof PackageImportNotDefinedError && error.code === 'ERR_PACKAGE_IMPORT_NOT_DEFINED',
  );
});

test('supports custom extension order', () => {
  const root = makeProject({
    'src/foo.js': '',
    'src/foo.ts': '',
  });
  const basedir = path.join(root, 'src');

  const tsFirst = new Resolver({ basedir, extensions: ['.ts', '.js'] });
  assert.equal(tsFirst.resolve('./foo'), path.join(root, 'src/foo.ts'));

  const jsFirst = new Resolver({ basedir, extensions: ['.js', '.ts'] });
  assert.equal(jsFirst.resolve('./foo'), path.join(root, 'src/foo.js'));
});

test('preserveSymlinks controls realpath of resolved files', () => {
  const root = makeProject({
    'app/node_modules/.keep': '',
    'app/packages/real/package.json': { main: 'index.js' },
    'app/packages/real/index.js': '',
  });
  const app = path.join(root, 'app');
  const link = path.join(app, 'node_modules/linked');
  fs.symlinkSync(path.join(app, 'packages/real'), link, 'dir');

  const defaultResolver = new Resolver({ basedir: app });
  assert.equal(defaultResolver.resolve('linked'), path.join(app, 'packages/real/index.js'));

  const preserved = new Resolver({ basedir: app, preserveSymlinks: true });
  assert.equal(preserved.resolve('linked'), path.join(app, 'node_modules/linked/index.js'));
});

test('throws MODULE_NOT_FOUND for missing specifiers', () => {
  const root = makeProject({ 'app/index.js': '' });
  const basedir = path.join(root, 'app');

  assert.throws(
    () => resolveSync('does-not-exist', { basedir }),
    (error) => error.code === 'MODULE_NOT_FOUND' && error.request === 'does-not-exist',
  );
});
