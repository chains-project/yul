import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveColorSupport, describeColorSupport } from '../src/color-support.js';

const truecolor = { level: 3, hasBasic: true, has256: true, has16m: true };
const detected = truecolor;

test('describeColorSupport reports none when unsupported', () => {
  assert.equal(describeColorSupport(false), 'none');
  assert.equal(describeColorSupport(undefined), 'none');
});

test('describeColorSupport reports basic colors', () => {
  assert.equal(
    describeColorSupport({ hasBasic: true, has256: false, has16m: false }),
    'basic (16 colors)',
  );
});

test('describeColorSupport reports 256 colors', () => {
  assert.equal(
    describeColorSupport({ hasBasic: true, has256: true, has16m: false }),
    '256 colors',
  );
});

test('describeColorSupport reports truecolor', () => {
  assert.equal(describeColorSupport(truecolor), 'truecolor (16m)');
});

test('keeps detected support when there are no overrides', () => {
  assert.equal(resolveColorSupport({ detected }), detected);
});

test('NO_COLOR with a value disables color', () => {
  assert.equal(resolveColorSupport({ detected, env: { NO_COLOR: '1' } }), false);
});

test('an empty NO_COLOR does not disable color', () => {
  assert.equal(resolveColorSupport({ detected, env: { NO_COLOR: '' } }), detected);
});

test('FORCE_COLOR overrides NO_COLOR', () => {
  assert.equal(
    resolveColorSupport({ detected, env: { NO_COLOR: '1', FORCE_COLOR: '3' } }),
    detected,
  );
});

test('an explicit --color flag overrides NO_COLOR', () => {
  assert.equal(
    resolveColorSupport({ detected, env: { NO_COLOR: '1' }, argv: ['node', 'cli', '--color'] }),
    detected,
  );
});
