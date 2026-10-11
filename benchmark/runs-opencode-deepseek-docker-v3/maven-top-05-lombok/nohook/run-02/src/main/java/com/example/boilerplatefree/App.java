package com.example.boilerplatefree;

import com.example.boilerplatefree.model.User;
import lombok.extern.java.Log;

import java.time.Instant;
import java.util.List;

@Log
public class App {

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .username("ada")
                .email("ada@example.com")
                .passwordHash("s3cr3t")
                .roles(List.of("ADMIN", "USER"))
                .createdAt(Instant.now())
                .build();

        log.info("Created user: " + user);

        user.setEmail("ada.lovelace@example.com");
        log.info("isAdmin=" + user.isAdmin() + ", email=" + user.getEmail());
    }
}
