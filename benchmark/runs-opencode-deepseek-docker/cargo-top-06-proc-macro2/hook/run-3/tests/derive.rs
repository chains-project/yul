use token_wrapper::FieldNames;

#[derive(FieldNames)]
#[allow(dead_code)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(FieldNames)]
#[allow(dead_code)]
struct Pair(u8, u8);

#[test]
fn derive_expands_for_named_fields() {
    assert_eq!(Point::FIELD_NAMES, &["x", "y"]);
}

#[test]
fn derive_expands_for_unnamed_fields() {
    assert_eq!(Pair::FIELD_NAMES, &["0", "1"]);
}
