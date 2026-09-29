package com.example.app;

import com.example.app.model.User;
import com.example.app.service.UserService;
import com.example.app.service.UserService.UserRepository;

public class App {

    public static void main(String[] args) {
        UserService service = new UserService(new UserRepository());
        User user = service.register("jane", "jane@example.com");
        System.out.println(user);
    }
}
