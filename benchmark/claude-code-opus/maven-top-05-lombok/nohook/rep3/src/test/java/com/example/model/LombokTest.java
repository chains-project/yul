package com.example.model;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class LombokTest {

    @Test
    void userHasGeneratedAccessorsBuilderAndEquality() {
        User user = User.builder().id(1L).name("Ada").email("ada@example.com").build();
        user.setName("Ada Lovelace");

        assertEquals("Ada Lovelace", user.getName());
        assertEquals(new User(1L, "Ada Lovelace", "ada@example.com"), user);
    }

    @Test
    void moneyIsImmutableAndNullChecked() {
        Money money = new Money(new BigDecimal("9.99"), "EUR");

        assertEquals("EUR", money.getCurrency());
        assertThrows(NullPointerException.class, () -> new Money(null, "EUR"));
    }
}
