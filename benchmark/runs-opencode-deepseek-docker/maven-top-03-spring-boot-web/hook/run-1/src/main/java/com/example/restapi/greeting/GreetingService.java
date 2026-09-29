package com.example.restapi.greeting;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final AtomicLong counter = new AtomicLong();
    private final Map<Long, Greeting> greetings = new ConcurrentHashMap<>();

    public Greeting create(String name) {
        long id = counter.incrementAndGet();
        Greeting greeting = new Greeting(id, "Hello, %s!".formatted(name));
        greetings.put(id, greeting);
        return greeting;
    }

    public Greeting findById(long id) {
        Greeting greeting = greetings.get(id);
        if (greeting == null) {
            throw new GreetingNotFoundException(id);
        }
        return greeting;
    }

    public List<Greeting> findAll() {
        return List.copyOf(greetings.values());
    }
}
