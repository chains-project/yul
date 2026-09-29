package com.example

fun main(args: Array<String>) {
    println(greeting(args.firstOrNull()))

    // AutoCloseable.use is provided by kotlin-stdlib-jdk7.
    val resource = AutoCloseable { println("closed") }
    resource.use { println("Using a JDK 7 AutoCloseable") }
}

fun greeting(name: String? = null): String =
    if (name == null) "Hello, JDK 7!" else "Hello, $name!"
