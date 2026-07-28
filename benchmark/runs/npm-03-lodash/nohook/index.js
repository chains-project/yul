const _ = require('lodash');

const users = [
  { name: 'Alice', age: 28 },
  { name: 'Bob', age: 34 },
  { name: 'Carol', age: 22 },
];

const sortedByAge = _.sortBy(users, 'age');
const names = _.map(users, 'name');
const chunked = _.chunk(names, 2);

console.log('Sorted by age:', sortedByAge);
console.log('Names:', names);
console.log('Chunked:', chunked);
