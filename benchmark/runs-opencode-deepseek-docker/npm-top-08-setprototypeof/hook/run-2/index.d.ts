'use strict';

declare function setPrototypeOf<T>(obj: T, proto: object | null): T;

declare namespace setPrototypeOf {
  const strategy: 'native' | '__proto__' | 'copy';
}

export = setPrototypeOf;
