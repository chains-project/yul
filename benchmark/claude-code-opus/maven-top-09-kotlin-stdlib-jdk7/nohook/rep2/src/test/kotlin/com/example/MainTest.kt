package com.example

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class MainTest {
    @Test
    fun firstLineReturnsFirstLine() {
        assertEquals("one", firstLine("one\ntwo"))
    }

    @Test
    fun firstLineOfEmptyTextIsNull() {
        assertNull(firstLine(""))
    }
}
