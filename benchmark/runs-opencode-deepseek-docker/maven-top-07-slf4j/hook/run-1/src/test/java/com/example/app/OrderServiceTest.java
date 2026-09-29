package com.example.app;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class OrderServiceTest {

    private final OrderService service = new OrderService();

    @Test
    void placesValidOrder() {
        assertDoesNotThrow(() -> service.placeOrder("ABC-123", 2));
    }

    @Test
    void rejectsNonPositiveQuantity() {
        assertThrows(IllegalArgumentException.class, () -> service.placeOrder("ABC-123", 0));
    }
}
