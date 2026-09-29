#![allow(dead_code)]

use syn_transform::{trace, TypeInfo};

#[derive(TypeInfo)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(TypeInfo)]
struct Pair(i32, i32);

#[derive(TypeInfo)]
enum Shape {
    Circle,
    Square,
}

#[test]
fn inspects_struct_fields() {
    assert_eq!(Point::type_name(), "Point");
    assert_eq!(Point::field_names(), &["x", "y"]);
}

#[test]
fn inspects_tuple_and_enum() {
    assert_eq!(Pair::field_names(), &["0", "1"]);
    assert_eq!(Shape::field_names(), &["Circle", "Square"]);
}

#[trace]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[trace]
fn parse_and_rebuild() -> i32 {
    (1..=4).sum()
}

#[test]
fn transforms_function_body() {
    assert_eq!(add(1, 2), 3);
    assert_eq!(parse_and_rebuild(), 10);
}
