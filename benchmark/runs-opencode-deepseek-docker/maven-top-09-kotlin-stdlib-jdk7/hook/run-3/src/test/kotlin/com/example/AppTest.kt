package com.example

import org.junit.Assert.assertEquals
import org.junit.Test

class AppTest {
    @Test
    fun defaultGreeting() {
        assertEquals("Hello, JDK 7!", greeting())
    }

    @Test
    fun greetingWithName() {
        assertEquals("Hello, Kotlin!", greeting("Kotlin"))
    }
}
