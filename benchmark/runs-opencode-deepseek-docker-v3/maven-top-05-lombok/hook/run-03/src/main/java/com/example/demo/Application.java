package com.example.demo;

import com.example.demo.model.User;
import java.time.Instant;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class Application {

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .username("ada")
                .email("ada@example.com")
                .createdAt(Instant.now())
                .build();

        log.info("Created user: {}", user);
    }
}
