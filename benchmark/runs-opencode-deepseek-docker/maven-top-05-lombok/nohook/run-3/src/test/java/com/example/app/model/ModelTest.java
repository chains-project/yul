package com.example.app.model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;

import org.junit.jupiter.api.Test;

class ModelTest {

    @Test
    void dataGeneratesAccessorsAndValueSemantics() {
        User user = User.builder().id(1L).username("ada").email("ada@example.com").active(true).build();

        user.setEmail("ada.lovelace@example.com");
        assertEquals("ada.lovelace@example.com", user.getEmail());

        User same = new User(1L, "ada", "ada.lovelace@example.com", true);
        assertEquals(user, same);
        assertEquals(user.hashCode(), same.hashCode());

        User different = User.builder().id(2L).username("grace").build();
        assertNotEquals(user, different);
    }

    @Test
    void valueIsImmutableAndWithReturnsCopies() {
        Product product = Product.builder()
                .sku("SKU-1")
                .name("Keyboard")
                .price(new BigDecimal("49.99"))
                .quantity(3)
                .build();

        Product discounted = product.withPrice(new BigDecimal("39.99"));

        assertNotSame(product, discounted);
        assertEquals(new BigDecimal("49.99"), product.getPrice());
        assertEquals(new BigDecimal("39.99"), discounted.getPrice());
        assertEquals(product.getSku(), discounted.getSku());
        assertTrue(product.toString().contains("Keyboard"));
    }
}
