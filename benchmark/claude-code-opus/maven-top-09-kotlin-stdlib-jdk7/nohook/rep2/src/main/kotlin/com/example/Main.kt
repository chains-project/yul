package com.example

import java.io.StringReader

/** Reads the first line of [text] using `use`, which closes the reader via JDK 7's AutoCloseable support. */
fun firstLine(text: String): String? = StringReader(text).buffered().use { it.readLine() }

fun main() {
    println("Hello from Kotlin ${KotlinVersion.CURRENT} on Java ${System.getProperty("java.version")}")
    println("First line: ${firstLine("one\ntwo")}")
}
