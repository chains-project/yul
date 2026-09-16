package com.example

fun main() {
    val numbers = listOf(1, 2, 3, 4, 5)
    val sum = numbers.sum()
    println("Sum: $sum")

    val names = listOf("Alice", "Bob", "Charlie")
    val upper = names.map { it.uppercase() }
    println("Names: $upper")
}