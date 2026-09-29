package com.example.app;

import com.example.app.model.User;

public class App {

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .name("Ada Lovelace")
                .email("ada@example.com")
                .build();

        System.out.println(user);
    }
}
