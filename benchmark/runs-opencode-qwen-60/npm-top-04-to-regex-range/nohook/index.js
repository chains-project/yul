import { toRegexRange } from "to-regex-range";

function rangeToRegex(start, end) {
  const pattern = toRegexRange(start, end, { capture: true });
  return new RegExp(`^(${pattern})$`);
}

console.log(rangeToRegex(1, 100));
console.log("1".match(rangeToRegex(1, 100)) ? "✓ matches" : "✗ no match");
console.log("42".match(rangeToRegex(1, 100)) ? "✓ matches" : "✗ no match");
console.log("101".match(rangeToRegex(1, 100)) ? "✗ matches" : "✓ no match");