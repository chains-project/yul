'use strict';

var setPrototypeOf = Object.setPrototypeOf || ({ __proto__: [] } instanceof Array ? setProtoOf : mixinProperties);

module.exports = setPrototypeOf;

function setProtoOf(obj, proto) {
	obj.__proto__ = proto;
	return obj;
}

function mixinProperties(obj, proto) {
	for (var prop in proto) {
		if (!Object.prototype.hasOwnProperty.call(obj, prop)) {
			obj[prop] = proto[prop];
		}
	}
	return obj;
}
