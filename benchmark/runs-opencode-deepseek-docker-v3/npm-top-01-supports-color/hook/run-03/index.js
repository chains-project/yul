import {createSupportsColor} from 'supports-color';

/**
 * Color support for the current stdout stream.
 * `level` is 0 (none), 1 (basic), 2 (256 colors) or 3 (truecolor).
 */
export const colorSupport = createSupportsColor(process.stdout) || {
	level: 0,
	hasBasic: false,
	has256: false,
	has16m: false,
};

export const level = colorSupport.level;
export const hasColor = level > 0;
export const hasBasic = colorSupport.hasBasic;
export const has256 = colorSupport.has256;
export const has16m = colorSupport.has16m;

const wrap = (open, close) => text => {
	const value = String(text);
	return hasColor ? `\u001B[${open}m${value}\u001B[${close}m` : value;
};

export const red = wrap(31, 39);
export const green = wrap(32, 39);
export const yellow = wrap(33, 39);
export const blue = wrap(34, 39);
export const magenta = wrap(35, 39);
export const cyan = wrap(36, 39);
export const bold = wrap(1, 22);
export const dim = wrap(2, 22);

export default {
	level,
	hasColor,
	hasBasic,
	has256,
	has16m,
};
