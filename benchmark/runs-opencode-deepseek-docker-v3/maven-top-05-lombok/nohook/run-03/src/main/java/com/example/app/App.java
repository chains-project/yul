package com.example.app;

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
