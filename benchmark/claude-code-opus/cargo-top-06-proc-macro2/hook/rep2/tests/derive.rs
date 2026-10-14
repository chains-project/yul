use my_macros::TypeName;

#[derive(TypeName)]
struct Widget;

#[derive(TypeName)]
#[allow(dead_code)]
enum Shape<T> {
    Circle(T),
}

#[test]
fn derive_works() {
    assert_eq!(Widget::type_name(), "Widget");
    assert_eq!(Shape::<u8>::type_name(), "Shape");
}
