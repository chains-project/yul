'use strict';

const POW10 = (n) => Math.pow(10, n);

function isInt(value) {
  return Number.isInteger(value);
}

function digitClass(lo, hi) {
  if (lo === hi) return String(lo);
  if (lo === 0 && hi === 9) return '[0-9]';
  return `[${lo}-${hi}]`;
}

function fixedPattern(lo, hi, width) {
  if (lo === hi) return String(lo).padStart(width, '0');

  if (lo === 0 && hi === POW10(width) - 1) {
    return width === 1 ? '[0-9]' : `[0-9]{${width}}`;
  }

  if (width === 1) return digitClass(lo, hi);

  const step = POW10(width - 1);
  const firstLo = Math.floor(lo / step);
  const firstHi = Math.floor(hi / step);

  const groups = [];
  for (let d = firstLo; d <= firstHi; d++) {
    const base = d * step;
    const subLo = d === firstLo ? lo - base : 0;
    const subHi = d === firstHi ? hi - base : step - 1;
    const sub = fixedPattern(subLo, subHi, width - 1);
    const last = groups[groups.length - 1];
    if (last && last.sub === sub && last.end === d - 1) {
      last.end = d;
    } else {
      groups.push({ start: d, end: d, sub });
    }
  }

  const alternatives = groups.map((g) => digitClass(g.start, g.end) + g.sub);
  return alternatives.length === 1 ? alternatives[0] : `(?:${alternatives.join('|')})`;
}

function positivePattern(lo, hi) {
  if (lo > hi) return null;
  if (lo === hi) return String(lo);

  const parts = [];
  for (let width = 1; ; width++) {
    const wLo = Math.max(lo, width === 1 ? 0 : POW10(width - 1));
    const wHi = Math.min(hi, POW10(width) - 1);
    if (wLo <= wHi) parts.push(fixedPattern(wLo, wHi, width));
    if (POW10(width) - 1 >= hi) break;
  }

  return parts.length === 1 ? parts[0] : `(?:${parts.join('|')})`;
}

function toRegexRange(min, max, options = {}) {
  if (max === undefined) {
    max = min;
  }

  min = Number(min);
  max = Number(max);

  if (!isInt(min) || !isInt(max)) {
    throw new TypeError('toRegexRange: expected integer arguments');
  }

  if (min > max) {
    [min, max] = [max, min];
  }

  const alternatives = [];

  if (min < 0) {
    const negHi = Math.min(max, -1);
    const abs = positivePattern(Math.abs(negHi), Math.abs(min));
    alternatives.push(abs === null ? '' : `-${abs}`);
  }

  if (max >= 0) {
    alternatives.push(positivePattern(Math.max(min, 0), max));
  }

  let pattern = alternatives.length === 1 ? alternatives[0] : `(?:${alternatives.join('|')})`;

  const { capture = false, anchor = false } = options;
  if (capture) {
    pattern = `(${pattern})`;
  }
  if (anchor) {
    pattern = `^${pattern}$`;
  }

  return pattern;
}

module.exports = toRegexRange;
module.exports.toRegexRange = toRegexRange;
