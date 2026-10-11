//! Example crate exercising the `rust-transform-macro` procedural macros.

use rust_transform_macro::{double_literals, double_literals_in_file};

/// The attribute macro rewrites `21` into `42` at compile time.
#[double_literals]
pub fn answer() -> i32 {
    21
}

double_literals_in_file! {
    /// The function-like macro rewrites `10` and `1` into `20` and `2`.
    pub fn computed() -> i32 {
        10 + 1
    }
}
