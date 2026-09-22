const toRegexRange = require('to-regex-range');

function rangeToRegex(range, options = {}) {
  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(String(range));

  if (!match) {
    throw new TypeError(`Invalid range: ${range}`);
  }

  const [, min, max] = match;
  const source = toRegexRange(min, max, options);

  return new RegExp(`^(${source})$`);
}

if (require.main === module) {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }

  try {
    const regex = rangeToRegex(input);
    console.log(regex.source);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}

module.exports = rangeToRegex;
