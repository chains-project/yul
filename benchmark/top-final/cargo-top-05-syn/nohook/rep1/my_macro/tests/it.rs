use my_macro::Describe;

#[derive(Describe)]
struct Point {
    x: i32,
    y: i32,
}

#[test]
fn describes_fields() {
    assert_eq!(Point::describe(), &["x", "y"]);
}
