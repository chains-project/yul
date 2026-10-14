use work_macros::TypeName;

#[derive(TypeName)]
struct Widget;

#[derive(TypeName)]
#[allow(dead_code)]
struct Wrapper<T: Clone> {
    inner: T,
}

#[test]
fn derive_type_name() {
    assert_eq!(Widget::type_name(), "Widget");
    assert_eq!(Wrapper::<u8>::type_name(), "Wrapper");
}
