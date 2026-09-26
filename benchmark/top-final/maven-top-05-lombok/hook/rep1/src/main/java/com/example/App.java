package com.example;

import com.example.model.User;

public class App {
    public static void main(String[] args) {
        User user = new User(1L, "Ada Lovelace", "ada@example.com");
        System.out.println(user);
    }
}
