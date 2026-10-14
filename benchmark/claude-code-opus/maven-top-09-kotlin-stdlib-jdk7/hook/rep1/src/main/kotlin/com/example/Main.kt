package com.example

import java.io.BufferedReader
import java.io.StringReader

fun greet(name: String): String = "Hello, $name!"

/** Counts lines using `use`, which closes the reader via kotlin-stdlib-jdk7's AutoCloseable support. */
fun countLines(text: String): Int =
    BufferedReader(StringReader(text)).use { reader -> reader.readLines().size }

fun main(args: Array<String>) {
    println(greet(args.firstOrNull() ?: "World"))
}
