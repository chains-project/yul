use macros::saturating;

#[saturating]
fn compute(a: u8, b: u8, c: u8) -> u8 {
    a * b + c - 1
}

#[test]
fn saturates_instead_of_overflowing() {
    assert_eq!(compute(2, 3, 4), 9);
    assert_eq!(compute(100, 100, 0), u8::MAX - 1);
    assert_eq!(compute(0, 0, 0), 0);
}
