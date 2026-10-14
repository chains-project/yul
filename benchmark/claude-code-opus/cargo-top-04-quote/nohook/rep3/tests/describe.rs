use codegen_macros::Describe;

#[derive(Describe)]
struct Unit;

#[derive(Describe)]
struct Generic<T: Clone> {
    _value: T,
}

#[test]
fn derives_describe() {
    assert_eq!(Unit::describe(), "Unit");
    assert_eq!(Generic::<u8>::describe(), "Generic");
}
