use codegen_macros::{Describe, make_constants};

#[derive(Describe)]
struct Point {
    #[allow(dead_code)]
    x: i32,
    #[allow(dead_code)]
    y: i32,
}

#[derive(Describe)]
struct Unit;

make_constants!(alpha = 1, beta = 2);

#[test]
fn derive_describe_works() {
    assert_eq!(Point::describe(), "Point { x, y }");
    assert_eq!(Unit::describe(), "Unit");
}

#[test]
fn make_constants_works() {
    assert_eq!(alpha(), 1);
    assert_eq!(BETA, 2);
}
