const toRegexRange = require('to-regex-range');

function rangeToRegex(input) {
  const [min, max] = input.split('-').map(Number);
  const pattern = toRegexRange(min, max);
  return new RegExp(`^${pattern}$`);
}

if (require.main === module) {
  const input = process.argv[2];
  if (!input) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }
  const regex = rangeToRegex(input);
  console.log(regex.source);
}

module.exports = rangeToRegex;
