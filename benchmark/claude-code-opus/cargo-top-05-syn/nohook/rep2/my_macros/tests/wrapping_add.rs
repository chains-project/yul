use my_macros::wrapping_add;

#[wrapping_add]
fn add(a: u8, b: u8, c: u8) -> u8 {
    a + b + c
}

#[test]
fn wraps_instead_of_panicking() {
    assert_eq!(add(1, 2, 3), 6);
    assert_eq!(add(250, 5, 10), 9);
}
