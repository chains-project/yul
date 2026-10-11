package com.example

import java.nio.file.Files
import java.nio.file.Paths

class Resource : AutoCloseable {
    override fun close() = println("resource closed")
}

fun main() {
    Resource().use {
        println("Hello from Kotlin on JDK 7")
    }

    val path = Paths.get(".")
    try {
        println("Working directory exists: " + Files.exists(path))
    } catch (e: Exception) {
        println(e.message)
    }
}
