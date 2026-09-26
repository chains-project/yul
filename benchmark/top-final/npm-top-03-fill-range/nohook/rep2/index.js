const fill = require('fill-range');

function expandRange(range) {
  const [start, end] = range.split('-');
  return fill(start, end);
}

module.exports = expandRange;

if (require.main === module) {
  const range = process.argv[2];
  if (!range) {
    console.error('Usage: node index.js <range>  (e.g. 1-10 or a-z)');
    process.exit(1);
  }
  console.log(expandRange(range));
}
