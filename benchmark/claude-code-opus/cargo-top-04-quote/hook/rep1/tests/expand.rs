use codegen_macros::{Describe, getters};

#[derive(Describe)]
struct Named {
    _a: u8,
    _b: String,
}

#[derive(Describe)]
struct Tuple(#[allow(dead_code)] u8, #[allow(dead_code)] u8);

#[derive(Describe)]
struct Unit;

#[getters]
struct Config<T> {
    name: String,
    value: T,
}

#[test]
fn describe() {
    assert_eq!(Named::describe(), "Named { _a, _b }");
    assert_eq!(Tuple::describe(), "Tuple { 0, 1 }");
    assert_eq!(Unit::describe(), "Unit");
}

#[test]
fn getters() {
    let c = Config { name: "x".into(), value: 42 };
    assert_eq!(c.get_name(), "x");
    assert_eq!(*c.get_value(), 42);
}
