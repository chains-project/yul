use my_macros::checked_arith;

#[checked_arith]
fn compute(a: u8, b: u8, c: u8) -> u8 {
    a * b + c - 1
}

#[test]
fn computes_without_overflow() {
    assert_eq!(compute(2, 3, 4), 9);
}

#[test]
#[should_panic(expected = "arithmetic overflow")]
fn panics_on_overflow() {
    compute(200, 2, 0);
}

#[test]
#[should_panic(expected = "arithmetic overflow")]
fn panics_on_underflow() {
    compute(0, 0, 0);
}
