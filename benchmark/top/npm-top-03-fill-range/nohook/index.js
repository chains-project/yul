const fill = require('fill-range');

function expandRange(range) {
  const [start, end] = range.split('-');
  return fill(start, end);
}

// Example usage
console.log(expandRange('1-10'));
console.log(expandRange('a-z'));
