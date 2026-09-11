const toRegexRange = require('to-regex-range');

function rangeToRegex(rangeStr) {
  const [min, max] = rangeStr.split('-').map(Number);
  const pattern = toRegexRange(min, max);
  return new RegExp(`^${pattern}$`);
}

const range = process.argv[2] || '1-100';
const regex = rangeToRegex(range);
console.log(`Range: ${range}`);
console.log(`Regex: ${regex}`);
