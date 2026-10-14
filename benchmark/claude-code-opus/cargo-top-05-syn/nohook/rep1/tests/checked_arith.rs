use syntax_macros::checked_arith;

#[checked_arith]
fn compute(a: u8, b: u8) -> u8 {
    a * 2 + b
}

#[test]
fn computes_in_range() {
    assert_eq!(compute(10, 5), 25);
}

#[test]
#[should_panic(expected = "attempt to multiply with overflow")]
fn panics_on_overflow() {
    compute(200, 0);
}
