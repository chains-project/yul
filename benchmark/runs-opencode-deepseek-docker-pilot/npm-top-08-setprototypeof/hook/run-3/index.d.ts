declare function setPrototypeOf<T extends object>(
  obj: T,
  proto: object | null
): T;

declare namespace setPrototypeOf {
  export { setPrototypeOf };
}

export = setPrototypeOf;
