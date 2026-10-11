import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fileURLToPath} from 'node:url';

const execFileAsync = promisify(execFile);
const cli = fileURLToPath(new URL('../bin/cli.js', import.meta.url));

const run = (env, args = []) =>
	execFileAsync(process.execPath, [cli, ...args], {env: {...process.env, ...env}});

test('emits ANSI escapes when FORCE_COLOR=1', async () => {
	const {stdout} = await run({FORCE_COLOR: '1'});
	assert.match(stdout, /\u001B\[/);
});

test('omits ANSI escapes when FORCE_COLOR=0', async () => {
	const {stdout} = await run({FORCE_COLOR: '0'});
	assert.doesNotMatch(stdout, /\u001B\[/);
});

test('--json reports the detected level', async () => {
	const {stdout} = await run({FORCE_COLOR: '2'}, ['--json']);
	assert.deepEqual(JSON.parse(stdout), {
		level: 2,
		hasColor: true,
		hasBasic: true,
		has256: true,
		has16m: false,
	});
});
