package com.example.demo.service;

import com.example.demo.model.User;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class UserServiceTest {

    @Test
    void createAssignsIdAndStoresUser() {
        UserService service = new UserService();

        User user = service.create("alice", "alice@example.com");

        assertEquals(1L, user.getId());
        assertTrue(service.findById(1L).isPresent());
    }

    @Test
    void findByIdReturnsEmptyWhenMissing() {
        UserService service = new UserService();
        assertEquals(Optional.empty(), service.findById(999L));
    }

    @Test
    void findAllReflectsCreatedUsers() {
        UserService service = new UserService();
        assertTrue(service.findAll().isEmpty());

        service.create("alice", "alice@example.com");
        service.create("bob", "bob@example.com");

        assertEquals(2, service.findAll().size());
        assertFalse(service.findAll().isEmpty());
    }
}
