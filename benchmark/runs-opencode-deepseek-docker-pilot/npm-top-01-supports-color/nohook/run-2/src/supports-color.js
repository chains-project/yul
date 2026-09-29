/**
 * Color support levels.
 *
 * 0 - no color
 * 1 - basic 16 colors
 * 2 - 256 colors
 * 3 - 16 million colors (truecolor)
 */
export const ColorLevel = Object.freeze({
  NONE: 0,
  BASIC: 1,
  COLORS_256: 2,
  TRUECOLOR: 3,
});

/**
 * Parse the FORCE_COLOR value into a color level.
 *
 * Per https://force-color.org/, the presence of the variable forces color on.
 * An empty string or "true" means basic color, a number selects the level, and
 * "0" (or "false") disables color.
 */
function parseForceColor(value) {
  if (value === "0" || value === "false") return ColorLevel.NONE;
  if (value === "" || value === "true") return ColorLevel.BASIC;

  const level = Number(value);
  if (!Number.isFinite(level)) return ColorLevel.BASIC;

  return Math.min(Math.max(Math.trunc(level), ColorLevel.NONE), ColorLevel.TRUECOLOR);
}

/**
 * Convert the bit depth reported by `stream.getColorDepth()` into a level.
 */
function depthToLevel(depth) {
  if (depth >= 24) return ColorLevel.TRUECOLOR;
  if (depth >= 8) return ColorLevel.COLORS_256;
  if (depth >= 4) return ColorLevel.BASIC;
  return ColorLevel.NONE;
}

/**
 * Detect how much color the given stream supports.
 *
 * Honors the community standards:
 * - FORCE_COLOR overrides everything (https://force-color.org/)
 * - NO_COLOR disables color when present and non-empty (https://no-color.org/)
 * - TERM=dumb disables color
 *
 * Falls back to `stream.getColorDepth()` when available, so that the terminal's
 * advertised capabilities and CI environment are taken into account.
 *
 * @param {object} [options]
 * @param {NodeJS.ProcessEnv} [options.env=process.env]
 * @param {NodeJS.WriteStream} [options.stream=process.stdout]
 * @returns {number} one of the ColorLevel values
 */
export function detectColorLevel({ env = process.env, stream = process.stdout } = {}) {
  if (env.FORCE_COLOR !== undefined) {
    return parseForceColor(env.FORCE_COLOR);
  }

  if (typeof env.NO_COLOR === "string" && env.NO_COLOR !== "") {
    return ColorLevel.NONE;
  }

  if (env.TERM === "dumb") {
    return ColorLevel.NONE;
  }

  if (!stream || stream.isTTY !== true) {
    return ColorLevel.NONE;
  }

  if (typeof stream.getColorDepth === "function") {
    return depthToLevel(stream.getColorDepth(env));
  }

  return ColorLevel.BASIC;
}

/**
 * Convenience wrapper: does the stream support at least `count` colors?
 *
 * @param {number} [count=2] minimum number of colors required
 * @param {object} [options] forwarded to `detectColorLevel`
 * @returns {boolean}
 */
export function supportsColor(count = 2, options) {
  return detectColorLevel(options) >= (count > 16 ? ColorLevel.COLORS_256 : ColorLevel.BASIC);
}
