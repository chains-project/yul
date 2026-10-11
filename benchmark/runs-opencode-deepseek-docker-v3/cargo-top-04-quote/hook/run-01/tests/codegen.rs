use codegen_macros::{CodeGen, make_struct};

#[derive(CodeGen)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(CodeGen)]
enum Color {
    Red,
    Green,
    Blue,
}

#[derive(CodeGen)]
struct Marker;

make_struct!(Pair {
    left: i32,
    right: i32,
});

#[test]
fn derives_struct_field_names() {
    assert_eq!(Point::FIELD_COUNT, 2);
    assert_eq!(Point::field_names(), &["x", "y"]);
}

#[test]
fn derives_enum_variant_names() {
    assert_eq!(Color::field_names(), &["Red", "Green", "Blue"]);
}

#[test]
fn derives_unit_struct() {
    assert_eq!(Marker::FIELD_COUNT, 0);
    assert!(Marker::field_names().is_empty());
}

#[test]
fn generated_types_are_usable() {
    let point = Point { x: 3, y: 4 };
    let colors = [Color::Red, Color::Green, Color::Blue];
    assert_eq!(point.x + point.y, 7);
    assert_eq!(colors.len(), 3);
}

#[test]
fn generated_struct_compiles_and_constructs() {
    let pair = Pair::new(1, 2);
    assert_eq!(pair, Pair { left: 1, right: 2 });
    assert_eq!(pair.left + pair.right, 3);
}
