//! Systems-tool library: native C interoperability plus safe wrappers.
//!
//! The crate links a bundled C library (`csrc/native.c`, compiled by
//! `build.rs`) and also calls libc directly. Raw bindings live in [`ffi`];
//! prefer the safe API re-exported from [`sys`].

pub mod ffi;
pub mod sys;

pub use sys::{cpu_count, fnv1a, hostname, page_size, parse_i64, pid, process_name, uid};
