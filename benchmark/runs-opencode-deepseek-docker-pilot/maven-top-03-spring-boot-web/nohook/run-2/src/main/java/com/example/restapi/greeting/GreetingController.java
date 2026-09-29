package com.example.restapi.greeting;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/greetings")
public class GreetingController {

    private final AtomicLong counter = new AtomicLong();
    private final List<Greeting> greetings = new CopyOnWriteArrayList<>();

    @GetMapping
    public List<Greeting> list() {
        return greetings;
    }

    @GetMapping("/{id}")
    public Greeting getById(@PathVariable Long id) {
        return greetings.stream()
                .filter(greeting -> greeting.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                        "Greeting %d not found".formatted(id)));
    }

    @PostMapping
    public ResponseEntity<Greeting> create(@Valid @RequestBody Greeting request) {
        Greeting created = new Greeting(counter.incrementAndGet(), request.content());
        greetings.add(created);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        boolean removed = greetings.removeIf(greeting -> greeting.id().equals(id));
        if (!removed) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND,
                    "Greeting %d not found".formatted(id));
        }
        return ResponseEntity.noContent().build();
    }
}
