const toRegexRange = require('to-regex-range');

function rangeToRegex(input) {
  const [min, max] = input.split('-').map(Number);
  return new RegExp(`^${toRegexRange(min, max)}$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }
  console.log(rangeToRegex(input).source);
}
