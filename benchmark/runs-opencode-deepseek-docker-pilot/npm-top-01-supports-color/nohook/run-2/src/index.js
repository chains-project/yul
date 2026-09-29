import { detectColorLevel, supportsColor, ColorLevel } from "./supports-color.js";
import { createColors } from "./colors.js";

export { detectColorLevel, supportsColor, createColors, ColorLevel };

/** Color level detected for the current `process.stdout`. */
export const colorLevel = detectColorLevel();

/** Ready-to-use formatters bound to the current `process.stdout`. */
export const colors = createColors(colorLevel);
