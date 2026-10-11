package com.example;

import com.example.model.User;

public final class App {

    private App() {
    }

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .name("Ada Lovelace")
                .email("ada@example.com")
                .build();

        System.out.println(user);
    }
}
