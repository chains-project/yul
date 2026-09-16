const fillRange = require('./index');

console.log('Testing fillRange function...\n');

// Test numeric ranges
console.log('1-10:', fillRange(1, 10));
console.log('Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]');
console.log();

console.log('1-5:', fillRange(1, 5));
console.log('Expected: [1, 2, 3, 4, 5]');
console.log();

console.log('10-1:', fillRange(10, 1));
console.log('Expected: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]');
console.log();

// Test alphabetic ranges
console.log('a-z:', fillRange('a', 'z'));
console.log('Expected: [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z]');
console.log();

console.log('A-Z:', fillRange('A', 'Z'));
console.log('Expected: [A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z]');
console.log();

console.log('a-e:', fillRange('a', 'e'));
console.log('Expected: [a, b, c, d, e]');
console.log();

// Test with step
console.log('1-10 step 2:', fillRange(1, 10, 2));
console.log('Expected: [1, 3, 5, 7, 9]');
console.log();

console.log('Test completed!');