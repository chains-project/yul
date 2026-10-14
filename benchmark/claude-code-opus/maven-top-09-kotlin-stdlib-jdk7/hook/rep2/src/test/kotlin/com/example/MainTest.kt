package com.example

import kotlin.test.Test
import kotlin.test.assertEquals

class MainTest {
    @Test
    fun greetsByName() {
        assertEquals("Hello, World!", greeting("World"))
    }
}
