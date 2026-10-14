use work_macros::passthrough;

#[test]
fn passthrough_expands_in_real_code() {
    passthrough!(let x = 1 + 2;);
    assert_eq!(x, 3);
}
