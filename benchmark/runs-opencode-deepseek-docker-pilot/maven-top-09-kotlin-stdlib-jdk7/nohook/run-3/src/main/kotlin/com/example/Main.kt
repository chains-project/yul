package com.example

import java.io.Closeable

private class Resource : Closeable {
    override fun close() = println("closed")
}

fun main(args: Array<String>) {
    println("Kotlin ${KotlinVersion.CURRENT} running on JDK 7 compatible bytecode")

    Resource().use {
        println("borrowed resource")
    }

    args.forEach { println("arg: $it") }
}
