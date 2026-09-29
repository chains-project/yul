use stable_macros::Describe;

#[derive(Describe)]
struct Widget;

#[derive(Describe)]
#[allow(dead_code)]
struct Holder<T> {
    value: T,
}

#[test]
fn derive_produces_describe() {
    assert_eq!(Widget::describe(), "Widget");
    assert_eq!(Holder::<u8>::describe(), "Holder");
}
