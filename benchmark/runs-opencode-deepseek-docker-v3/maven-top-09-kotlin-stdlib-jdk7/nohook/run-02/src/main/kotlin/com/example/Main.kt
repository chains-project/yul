package com.example

fun main(args: Array<String>) {
    println(greeting(args.firstOrNull() ?: "world"))
}

fun greeting(name: String): String = "Hello, $name!"
