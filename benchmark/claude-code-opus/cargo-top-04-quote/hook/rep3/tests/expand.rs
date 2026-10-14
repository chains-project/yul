use codegen_macros::{Describe, make_const};

#[derive(Describe)]
struct Named {
    _a: u8,
    _b: String,
}

#[allow(dead_code)]
#[derive(Describe)]
struct Tuple(u8, u16);

#[derive(Describe)]
struct Unit;

#[derive(Describe)]
struct Generic<T: Clone> {
    _inner: T,
}

make_const!(seven = 7);

#[test]
fn describe_named() {
    assert_eq!(Named::describe(), "Named { _a, _b }");
}

#[test]
fn describe_tuple_and_unit() {
    assert_eq!(Tuple::describe(), "Tuple { 0, 1 }");
    assert_eq!(Unit::describe(), "Unit");
}

#[test]
fn describe_generic() {
    assert_eq!(Generic::<i32>::describe(), "Generic { _inner }");
}

#[test]
fn make_const_generates_fn() {
    const V: i64 = seven_value();
    assert_eq!(V, 7);
}
