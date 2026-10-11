export = setPrototypeOf;

/**
 * Sets the prototype (i.e. the internal [[Prototype]] property) of the
 * specified object to another object or `null`.
 *
 * Uses the native `Object.setPrototypeOf` when available, falling back to the
 * `__proto__` setter and finally to a property-mixin approximation.
 */
declare function setPrototypeOf<T extends object>(obj: T, proto: object | null): T;

declare namespace setPrototypeOf {
	/** @internal Sets the prototype via the `__proto__` setter. */
	function setProtoOf<T extends object>(obj: T, proto: object | null): T;
	/** @internal Copies inherited enumerable properties as an approximation. */
	function mixinProperties<T extends object>(obj: T, proto: object | null): T;
	/** @internal Selects an implementation for the current runtime. */
	function createSetPrototypeOf(): typeof setPrototypeOf;
}
