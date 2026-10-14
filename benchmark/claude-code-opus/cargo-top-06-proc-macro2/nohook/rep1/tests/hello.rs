use my_macros::Hello;

#[derive(Hello)]
struct Widget;

#[test]
fn derive_hello_works() {
    assert_eq!(Widget::hello(), "Widget");
}
