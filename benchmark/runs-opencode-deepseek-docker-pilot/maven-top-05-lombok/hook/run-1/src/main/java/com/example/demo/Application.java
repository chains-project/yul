package com.example.demo;

import com.example.demo.model.User;
import java.util.List;

public class Application {

    public static void main(String[] args) {
        User user = User.builder()
                .id(1L)
                .name("Ada Lovelace")
                .email("ada@example.com")
                .roles(List.of("admin", "developer"))
                .build();

        System.out.println(user);
    }
}
