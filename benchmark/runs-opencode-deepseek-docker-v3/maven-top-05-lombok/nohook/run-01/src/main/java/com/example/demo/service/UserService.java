package com.example.demo.service;

import com.example.demo.model.User;
import lombok.RequiredArgsConstructor;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

@RequiredArgsConstructor
public class UserService {

    private final AtomicLong idGenerator = new AtomicLong();

    private final List<User> users = new ArrayList<>();

    public User create(String username, String email) {
        User user = User.builder()
                .id(idGenerator.incrementAndGet())
                .username(username)
                .email(email)
                .createdAt(Instant.now())
                .build();
        users.add(user);
        return user;
    }

    public Optional<User> findById(long id) {
        return users.stream()
                .filter(user -> user.getId() == id)
                .findFirst();
    }

    public List<User> findAll() {
        return List.copyOf(users);
    }
}
