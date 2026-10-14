declare function setPrototypeOf<T extends object>(obj: T, proto: object | null): T;

declare namespace setPrototypeOf {
  function setProtoOf<T extends object>(obj: T, proto: object | null): T;
  function mixinProperties<T extends object>(obj: T, proto: object | null): T;
}

export = setPrototypeOf;
