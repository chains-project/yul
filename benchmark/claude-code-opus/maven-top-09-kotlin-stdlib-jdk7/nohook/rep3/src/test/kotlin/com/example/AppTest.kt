package com.example

import kotlin.test.Test
import kotlin.test.assertEquals

class AppTest {
    @Test
    fun greetsByName() {
        assertEquals("Hello, Kotlin!", greet("Kotlin"))
    }

    @Test
    fun readsFirstLine() {
        assertEquals("one", firstLine("one\ntwo"))
    }
}
