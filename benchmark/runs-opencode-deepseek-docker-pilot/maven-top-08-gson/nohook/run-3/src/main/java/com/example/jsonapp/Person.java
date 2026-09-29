package com.example.jsonapp;

import java.util.List;

public record Person(String name, int age, List<String> hobbies) {
}
