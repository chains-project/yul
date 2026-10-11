use ast_transform::identifiers;

const NAMES: &[&str] = identifiers!(
    "pub fn add(a: i32, b: i32) -> i32 { a + b }\
     fn main() { let total = add(1, 2); assert_eq!(total, 3); }"
);

#[test]
fn lists_every_identifier() {
    for expected in ["add", "a", "b", "i32", "main", "total"] {
        assert!(NAMES.contains(&expected), "missing `{expected}`");
    }
}

#[test]
fn result_is_sorted_and_deduplicated() {
    let mut expected = NAMES.to_vec();
    expected.sort_unstable();
    expected.dedup();
    assert_eq!(NAMES, expected.as_slice());
}
