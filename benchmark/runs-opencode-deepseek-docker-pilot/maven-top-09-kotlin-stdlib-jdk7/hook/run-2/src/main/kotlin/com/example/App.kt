package com.example

class Resource(private val name: String) : AutoCloseable {
    fun read(): String = "resource: $name"

    override fun close() {
        println("closed $name")
    }
}

fun main(args: Array<String>) {
    Resource("demo").use { resource ->
        println(resource.read())
    }
}
