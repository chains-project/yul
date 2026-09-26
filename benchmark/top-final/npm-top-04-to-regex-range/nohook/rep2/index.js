const toRegexRange = require('to-regex-range');

function rangeToRegex(rangeStr) {
  const [min, max] = rangeStr.split('-').map(Number);
  return new RegExp(`^${toRegexRange(min, max)}$`);
}

module.exports = rangeToRegex;

if (require.main === module) {
  const rangeStr = process.argv[2];
  if (!rangeStr) {
    console.error('Usage: node index.js <min>-<max>');
    process.exit(1);
  }
  console.log(rangeToRegex(rangeStr).source);
}
