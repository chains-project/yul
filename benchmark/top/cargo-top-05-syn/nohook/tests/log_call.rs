use my_macro::log_call;

#[log_call]
fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[test]
fn it_works() {
    assert_eq!(add(2, 2), 4);
}
