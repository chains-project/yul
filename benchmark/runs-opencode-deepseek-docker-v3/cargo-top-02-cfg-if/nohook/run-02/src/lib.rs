//! Small, dependency-free building blocks for writing cross-platform libraries.
//!
//! Every `#[cfg(...)]` attribute in this crate lives inside a single private
//! `platform` module. The public API is identical on all targets, so downstream
//! never need to write their own conditional-compilation blocks.
//!
//! # Example
//!
//! ```
//! use platform_kit::{current, Family};
//!
//! let platform = current();
//! match platform.family {
//!     Family::Unix => assert_eq!(platform.path_separator, '/'),
//!     Family::Windows => assert_eq!(platform.path_separator, '\\'),
//!     _ => {}
//! }
//! ```

#![forbid(unsafe_code)]

mod platform;

pub use platform::{Family, Platform, current};
