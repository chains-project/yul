package com.example.boilerplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.math.BigDecimal;

import org.junit.jupiter.api.Test;

class ProductTest {

    @Test
    void builderAndAccessorsWork() {
        Product product = Product.builder()
                .name("Widget")
                .price(new BigDecimal("9.99"))
                .quantity(3)
                .build();

        assertEquals("Widget", product.getName());
        assertEquals(new BigDecimal("9.99"), product.getPrice());
        assertEquals(3, product.getQuantity());
    }

    @Test
    void settersAndEqualsWork() {
        Product a = new Product("Widget", new BigDecimal("9.99"), 3);
        Product b = new Product("Widget", new BigDecimal("9.99"), 3);
        Product c = new Product("Gadget", new BigDecimal("19.99"), 1);

        assertEquals(a, b);
        assertEquals(a.hashCode(), b.hashCode());
        assertNotEquals(a, c);

        b.setQuantity(5);
        assertEquals(5, b.getQuantity());
    }
}
