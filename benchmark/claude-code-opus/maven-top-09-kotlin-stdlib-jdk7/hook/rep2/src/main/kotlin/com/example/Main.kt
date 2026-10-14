package com.example

import java.io.StringReader

fun greeting(name: String): String = "Hello, $name!"

fun main(args: Array<String>) {
    // `use` on Closeable/AutoCloseable resources is part of the JDK 7 stdlib support
    val line = StringReader(greeting(args.firstOrNull() ?: "Kotlin")).buffered().use { it.readLine() }
    println(line)
}
