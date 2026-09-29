package com.example.demo;

import com.example.demo.model.User;

public class App {

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .username("ada")
                .email("ada@example.com")
                .build();

        user.setEmail("ada.lovelace@example.com");

        System.out.println(user);
    }
}
