const toRegexRange = require('to-regex-range');

function rangeToRegex(range) {
  const match = String(range).match(/^\s*(\d+)\s*-\s*(\d+)\s*$/);
  if (!match) {
    throw new Error(`Invalid range: ${range}`);
  }

  const min = Number(match[1]);
  const max = Number(match[2]);

  if (min > max) {
    throw new Error(`Invalid range: ${range} (min is greater than max)`);
  }

  return toRegexRange(min, max);
}

if (require.main === module) {
  const input = process.argv[2] || '1-100';

  try {
    const pattern = rangeToRegex(input);
    console.log(pattern);
  } catch (err) {
    console.error(err.message);
    process.exitCode = 1;
  }
}

module.exports = rangeToRegex;
