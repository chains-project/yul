package com.example

import kotlin.test.Test
import kotlin.test.assertEquals

class MainTest {
    @Test
    fun greetsByName() {
        assertEquals("Hello, Kotlin!", greet("Kotlin"))
    }

    @Test
    fun countsLines() {
        assertEquals(3, countLines("a\nb\nc"))
    }
}
