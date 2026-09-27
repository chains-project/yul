package com.example

import java.io.ByteArrayOutputStream

fun main(args: Array<String>) {
    val name = if (args.isNotEmpty()) args[0] else "world"
    println("Hello, $name! Running on JDK ${System.getProperty("java.version")}")
}

fun encode(value: String): ByteArray {
    val out = ByteArrayOutputStream()
    out.use { it.write(value.toByteArray(Charsets.UTF_8)) }
    return out.toByteArray()
}
