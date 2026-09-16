#!/usr/bin/env node

/**
 * Expand a range string like '1-10' or 'a-z' into an array of all values in between.
 * 
 * Examples:
 *   expandRange('1-5')      => ['1', '2', '3', '4', '5']
 *   expandRange('a-e')      => ['a', 'b', 'c', 'd', 'e']
 *   expandRange('A-F', true) => ['A', 'B', 'C', 'D', 'E', 'F']
 *   expandRange('00-05')    => ['00', '01', '02', '03', '04', '05']
 *   expandRange('10-1', true) => ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
 * 
 * @param {string} rangeStr - The range string (e.g., '1-10', 'a-z')
 * @param {boolean} [keepNumbers=true] - Whether to return numbers as numbers (not strings)
 * @param {boolean} [descending=false] - Whether to expand in descending order
 * @returns {Array<string|number>} Array of values in the range
 */
function expandRange(rangeStr, keepNumbers = true, descending = false) {
  if (typeof rangeStr !== 'string') {
    throw new TypeError('Range must be a string');
  }

  const rangeRegex = /^([a-zA-Z0-9]+)-([a-zA-Z0-9]+)$/;
  const match = rangeStr.match(rangeRegex);

  if (!match) {
    throw new Error(`Invalid range format: "${rangeStr}". Expected format: "start-end" (e.g., "1-10" or "a-z")`);
  }

  const startStr = match[1];
  const endStr = match[2];

  // Check if the range is numeric
  const isNumeric = /^\d+$/.test(startStr) && /^\d+$/.test(endStr);

  if (isNumeric) {
    const start = parseInt(startStr, 10);
    const end = parseInt(endStr, 10);
    const step = descending ? -1 : 1;
    const result = [];

    if (start < end && descending) {
      throw new Error('Descending order requires start > end');
    }
    if (start > end && !descending) {
      throw new Error('Ascending order requires start <= end');
    }

    // Determine padding based on the original string length
    const padLength = Math.max(startStr.length, endStr.length);

    for (let i = start; descending ? i >= end : i <= end; i += step) {
      const padded = String(i).padStart(padLength, '0');
      result.push(keepNumbers ? (i === start ? parseInt(startStr, 10) + (i - start) * step : i) : padded);
    }

    // If keepNumbers is false, use string values
    if (!keepNumbers) {
      const arr = [];
      for (let i = start; descending ? i >= end : i <= end; i += step) {
        arr.push(String(i).padStart(padLength, '0'));
      }
      return arr;
    }

    return result;
  } else {
    // Character range
    const startCode = startStr.charCodeAt(0);
    const endCode = endStr.charCodeAt(0);

    if (startCode > endCode && !descending) {
      throw new Error('Ascending order requires start <= end for characters');
    }
    if (startCode < endCode && descending) {
      throw new Error('Descending order requires start >= end for characters');
    }

    const result = [];
    const step = descending ? -1 : 1;

    for (let code = startCode; descending ? code >= endCode : code <= endCode; code += step) {
      result.push(String.fromCharCode(code));
    }

    return result;
  }
}

module.exports = expandRange;