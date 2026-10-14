use my_macros::checked_arith;

#[checked_arith]
fn poly(x: i32) -> i32 {
    x * x + 2 * x - 1
}

#[checked_arith]
fn add_u8(a: u8, b: u8) -> u8 {
    a + b
}

#[test]
fn computes_normally() {
    assert_eq!(poly(3), 14);
    assert_eq!(add_u8(200, 55), 255);
}

#[test]
#[should_panic(expected = "arithmetic overflow in `add_u8`")]
fn panics_on_overflow() {
    add_u8(200, 56);
}

#[test]
fn parses_outside_macro_context() {
    // syn also works on plain strings via proc_macro2, useful for unit tests.
    let f: syn::ItemFn = syn::parse_str("fn f() -> i32 { 1 + 2 }").unwrap();
    assert_eq!(f.sig.ident, "f");
    assert_eq!(f.block.stmts.len(), 1);
}
