package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class PersonRepositoryTests {

    @Autowired
    private PersonRepository personRepository;

    @Test
    void savesAndLoadsPerson() {
        Person saved = personRepository.save(new Person("Ada Lovelace"));

        Person found = personRepository.findById(saved.getId()).orElseThrow();

        assertThat(found.getName()).isEqualTo("Ada Lovelace");
    }
}
