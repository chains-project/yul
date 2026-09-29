use codegen_macros::{make_consts, Describe};

#[derive(Describe)]
struct Point {
    x: f32,
    y: f32,
}

#[test]
fn describe_lists_field_names() {
    let point = Point { x: 1.0, y: 2.0 };
    assert_eq!(point.describe(), &["x", "y"]);
}

make_consts!(alpha, beta);

#[test]
fn make_consts_generates_const_items() {
    assert_eq!(ALPHA, "alpha");
    assert_eq!(BETA, "beta");
}
