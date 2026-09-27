package com.example.app.service;

import com.example.app.model.User;
import java.util.ArrayList;
import java.util.List;
import lombok.RequiredArgsConstructor;
import lombok.extern.java.Log;

@Log
@RequiredArgsConstructor
public class UserService {

    private final UserRepository repository;

    public User register(String username, String email) {
        log.info(() -> "Registering user " + username);
        User user = User.builder()
                .username(username)
                .email(email)
                .build();
        return repository.save(user);
    }

    public static class UserRepository {

        private final List<User> users = new ArrayList<>();

        public User save(User user) {
            user.setId((long) users.size() + 1);
            users.add(user);
            return user;
        }
    }
}
