use macros::trace;

#[trace]
fn add(a: u8, b: u8) -> u8 {
    a + b
}

#[trace("custom label")]
fn add3(a: u8, b: u8, c: u8) -> u8 {
    a + b + c
}

#[test]
fn rewrites_addition_to_wrapping() {
    assert_eq!(add(250, 10), 4);
    assert_eq!(add3(200, 50, 10), 4);
}
