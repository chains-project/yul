import toRegexRange from "to-regex-range";

function rangeToRegex(rangeStr) {
  const [min, max] = rangeStr.split("-").map(Number);
  return new RegExp(`^${toRegexRange(min, max)}$`);
}

const input = process.argv[2];
if (!input) {
  console.error("Usage: node index.js <min>-<max>");
  process.exit(1);
}

const regex = rangeToRegex(input);
console.log(regex.source);
