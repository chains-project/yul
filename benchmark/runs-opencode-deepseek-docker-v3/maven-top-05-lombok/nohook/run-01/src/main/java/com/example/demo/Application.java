package com.example.demo;

import com.example.demo.model.User;
import com.example.demo.service.UserService;
import lombok.extern.java.Log;

@Log
public class Application {

    public static void main(String[] args) {
        UserService userService = new UserService();

        User user = userService.create("alice", "alice@example.com");
        log.info("Created user: " + user);

        user.setEmail("alice@newdomain.com");
        log.info("Updated user: " + user);
    }
}
