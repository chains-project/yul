#[test]
fn inspect_lists_top_level_items() {
    let names = syn_transform::inspect!(fn main() {} struct Foo; enum E { A });
    assert_eq!(names, "main, Foo, E");
}

#[test]
fn transform_renames_items() {
    syn_transform::transform!(a => b, fn a() -> i32 { 1 });
    assert_eq!(b(), 1);
}

#[test]
fn transform_renames_locals() {
    syn_transform::transform!(x => y, fn compute() -> i32 { let x = 41; x + 1 });
    assert_eq!(compute(), 42);
}
