package com.example

import java.io.StringReader

/** Reads the first line using `use`, the JDK 7 AutoCloseable extension from kotlin-stdlib-jdk7. */
fun firstLine(text: String): String? = StringReader(text).buffered().use { it.readLine() }

fun main() {
    println("Hello from Kotlin ${KotlinVersion.CURRENT}! First line: ${firstLine("one\ntwo")}")
}
