const { toRegexRange } = require('to-regex-range');

/**
 * Convert a numeric range string like '1-100' into a single regular expression
 * that matches any integer in that range.
 *
 * @param {string} rangeStr - A range string in the format 'start-end'
 * @returns {RegExp} - A regex matching any number in the given range
 */
function rangeToRegex(rangeStr) {
  const trimmed = rangeStr.trim();
  const match = trimmed.match(/^(\d+)\s*-\s*(\d+)$/);

  if (!match) {
    throw new Error(`Invalid range format: "${rangeStr}". Expected "start-end" (e.g. "1-100").`);
  }

  const start = Number(match[1]);
  const end = Number(match[2]);

  if (start > end) {
    throw new Error(`Start (${start}) is greater than end (${end}).`);
  }

  const regexPattern = toRegexRange(start, end);
  return new RegExp(`^${regexPattern}$`);
}

// If run directly, demonstrate with examples
if (require.main === module) {
  const ranges = ['1-10', '1-100', '0-5', '50-60', '100-120'];

  for (const range of ranges) {
    try {
      const regex = rangeToRegex(range);
      console.log(`Range "${range}" => Regex: /${regex.source}/`);
    } catch (err) {
      console.error(`Error for "${range}": ${err.message}`);
    }
  }
}

module.exports = { rangeToRegex };