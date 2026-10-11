package com.example.json;

import java.util.List;

public record Person(String name, int age, List<String> hobbies) {
}
