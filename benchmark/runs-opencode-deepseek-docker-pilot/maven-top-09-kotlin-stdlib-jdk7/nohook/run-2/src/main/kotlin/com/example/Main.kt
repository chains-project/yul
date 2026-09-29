package com.example

fun main(args: Array<String>) {
    println("Hello from Kotlin targeting JDK 7!")

    val resource = AutoCloseable { println("resource closed") }
    resource.use {
        println("using AutoCloseable.use from kotlin-stdlib-jdk7")
    }
}
