package com.example

import java.io.StringReader

fun greet(name: String): String = "Hello, $name!"

fun firstLine(text: String): String? =
    // `use` on AutoCloseable comes from kotlin-stdlib-jdk7
    StringReader(text).buffered().use { it.readLine() }

fun main(args: Array<String>) {
    println(greet(args.firstOrNull() ?: "World"))
}
