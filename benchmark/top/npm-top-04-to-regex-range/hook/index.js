const toRegexRange = require('to-regex-range');

function rangeToRegex(input) {
  const [start, end] = input.split('-').map(Number);
  const source = toRegexRange(start, end);
  return new RegExp(`^${source}$`);
}

if (require.main === module) {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: node index.js <start>-<end>');
    process.exit(1);
  }

  const regex = rangeToRegex(input);
  console.log(regex.source);
}

module.exports = rangeToRegex;
