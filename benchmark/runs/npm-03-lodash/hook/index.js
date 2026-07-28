const _ = require('lodash');

const users = [
  { user: 'barney', age: 36, active: true },
  { user: 'fred', age: 40, active: false },
  { user: 'pebbles', age: 1, active: true },
];

const activeUsers = _.filter(users, 'active');
console.log('Active users:', _.map(activeUsers, 'user'));

const grouped = _.groupBy(users, (u) => (u.age >= 18 ? 'adults' : 'minors'));
console.log('Grouped by age:', grouped);

console.log('Chunked:', _.chunk([1, 2, 3, 4, 5], 2));
console.log('Cloned deep:', _.cloneDeep(users));
