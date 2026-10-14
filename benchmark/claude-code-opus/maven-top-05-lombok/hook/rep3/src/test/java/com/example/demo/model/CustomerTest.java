package com.example.demo.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class CustomerTest {

    @Test
    void builderGettersAndSettersAreGenerated() {
        Customer customer = Customer.builder().id(1L).name("Ada").email("ada@example.com").build();

        customer.setName("Ada Lovelace");

        assertEquals(1L, customer.getId());
        assertEquals("Ada Lovelace", customer.getName());
        assertEquals("ada@example.com", customer.getEmail());
    }

    @Test
    void valueObjectHasConstructorAndEquality() {
        Address a = new Address("1 Main St", "London", "N1");
        Address b = new Address("1 Main St", "London", "N1");

        assertEquals(a, b);
        assertEquals("London", a.getCity());
    }
}
