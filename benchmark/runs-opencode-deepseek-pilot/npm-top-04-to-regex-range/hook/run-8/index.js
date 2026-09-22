const toRegexRange = require('to-regex-range');

function rangeToRegex(range) {
  const match = /^\s*(-?\d+)\s*-\s*(-?\d+)\s*$/.exec(String(range));
  if (!match) {
    throw new TypeError(`Invalid numeric range: ${range}`);
  }
  const [, min, max] = match;
  return new RegExp(`^(?:${toRegexRange(min, max)})$`);
}

if (require.main === module) {
  const range = process.argv[2];
  if (!range) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }
  console.log(rangeToRegex(range).source);
}

module.exports = rangeToRegex;
