'use strict';

const fs = require('fs');
const { promisify } = require('util');

const realpath = promisify(fs.realpath);

module.exports = { realpath };
