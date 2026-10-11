use codegen_macros::make_struct;

make_struct! {
    pub struct Point {
        pub x: f64,
        pub y: f64,
    }
}

make_struct! {
    pub struct Pair(pub i32, pub i32);
}

make_struct! {
    pub struct Marker;
}

#[test]
fn named_struct_constructor() {
    let point = Point::new(1.0, 2.0);
    assert_eq!(point.x, 1.0);
    assert_eq!(point.y, 2.0);
}

#[test]
fn tuple_struct_constructor() {
    let pair = Pair::new(3, 4);
    assert_eq!(pair.0, 3);
    assert_eq!(pair.1, 4);
}

#[test]
fn unit_struct_constructor() {
    let _marker = Marker::new();
}
