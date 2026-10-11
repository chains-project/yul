use codegen_macro::{define_enum, Describe};

#[derive(Describe)]
struct Point {
    x: i32,
    y: i32,
}

define_enum!(Color: Red, Green, Blue);

#[test]
fn describe_lists_fields() {
    let point = Point { x: 1, y: 2 };
    assert_eq!(point.describe(), vec!["x", "y"]);
    assert_eq!(point.x + point.y, 3);
}

#[test]
fn enum_name_roundtrips() {
    assert_eq!(Color::Green.name(), "Green");
    assert_eq!(Color::from_name("Blue"), Some(Color::Blue));
    assert_eq!(Color::from_name("Purple"), None);
}
