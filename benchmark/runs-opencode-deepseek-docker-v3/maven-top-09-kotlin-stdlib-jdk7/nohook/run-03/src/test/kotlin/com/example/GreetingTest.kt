package com.example

import kotlin.test.Test
import kotlin.test.assertEquals

class GreetingTest {
    @Test
    fun greetingMentionsJdk7() {
        assertEquals("Hello, Kotlin on JDK 7!", greeting())
    }
}
