import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

/**
 * Fixture tree, written to a temp dir at test time. Values: string = file
 * contents, object = JSON file, { symlink } = symlink target.
 */
export const tree = {
  'package.json': {
    name: 'project',
    exports: { '.': './main.js', './feature': './lib/feature.js' },
    imports: {
      '#internal/*': './src/internal/*.js',
      '#dep': 'exp-pkg',
      '#dep-sub/*': 'exp-pkg/sub/*',
      '#cond': { node: './src/node.js', default: './src/default.js' },
      '#escape': '../outside.js',
    },
  },
  'main.js': '',
  'lib/feature.js': '',
  'src/app.js': '',
  'src/internal/a.js': '',
  'src/node.js': '',
  'src/default.js': '',
  'src/data.json': '{}',
  'src/native.node': '',
  'src/only-file': '',
  'src/both.js': '',
  'src/both/index.js': '',
  'src/dir/index.js': '',
  'src/dir-with-main/package.json': { main: './entry' },
  'src/dir-with-main/entry.js': '',
  'src/main-dir/package.json': { main: 'lib' },
  'src/main-dir/lib/index.js': '',
  'src/bad-main/package.json': { main: './missing.js' },
  'src/bad-main/index.js': '',
  'src/broken-main/package.json': { main: './missing.js' },
  'src/bad-json/package.json': '{ not json',
  'src/bad-json/index.js': '',

  'node_modules/plain/index.js': '',
  'node_modules/main-pkg/package.json': { main: 'lib/m' },
  'node_modules/main-pkg/lib/m.js': '',
  'node_modules/main-pkg/other.js': '',
  'node_modules/exp-pkg/package.json': {
    name: 'exp-pkg',
    exports: {
      '.': { import: './esm.mjs', require: './cjs.js' },
      './sub/*': './dist/*.js',
      './sub/private/*': null,
      './data.json': './data.json',
      './pkg': './package.json',
      './bad': '../escape.js',
      './dotdot': './dist/../cjs.js',
      './arr': ['node:invalid', './cjs.js'],
      './missing': './does-not-exist.js',
      './dir/*': './dist/*',
    },
    imports: { '#self-internal': './dist/a.js' },
  },
  'node_modules/exp-pkg/cjs.js': '',
  'node_modules/exp-pkg/esm.mjs': '',
  'node_modules/exp-pkg/dist/a.js': '',
  'node_modules/exp-pkg/dist/private/x.js': '',
  'node_modules/exp-pkg/data.json': '{}',
  'node_modules/exp-pkg/notexported.js': '',
  'node_modules/sugar/package.json': { exports: './s.js' },
  'node_modules/sugar/s.js': '',
  'node_modules/conds/package.json': { exports: { 'module-sync': './sync.js', default: './def.js' } },
  'node_modules/conds/sync.js': '',
  'node_modules/conds/def.js': '',
  'node_modules/@scope/pkg/package.json': { exports: { './x': './x.js' } },
  'node_modules/@scope/pkg/x.js': '',
  'node_modules/@scope/legacy/index.js': '',
  'node_modules/mixed/package.json': { exports: { '.': './a.js', require: './b.js' } },
  'node_modules/mixed/a.js': '',
  'node_modules/pattern/package.json': {
    exports: {
      './*': './lib/*.js',
      './*.js': './lib/*.js',
      './features/*': './f/*/index.js',
      './features/internal/*': null,
    },
  },
  'node_modules/pattern/lib/foo.js': '',
  'node_modules/pattern/f/x/index.js': '',
  'node_modules/pattern/f/internal/y/index.js': '',
  'node_modules/linked': { symlink: '../linked-target' },
  'linked-target/index.js': '',

  'nested/deep/file.js': '',
  'nested/node_modules/plain/index.js': '',
};

export function createFixture() {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'resolver-fixture-')));
  const projectDir = path.join(root, 'project');
  for (const [rel, value] of Object.entries(tree)) {
    const abs = path.join(projectDir, rel);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    if (value && typeof value === 'object' && 'symlink' in value) {
      fs.symlinkSync(value.symlink, abs, 'dir');
    } else {
      fs.writeFileSync(abs, typeof value === 'string' ? value : JSON.stringify(value));
    }
  }
  return {
    root,
    projectDir,
    cleanup: () => fs.rmSync(root, { recursive: true, force: true }),
  };
}
