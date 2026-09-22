package com.example.demo.book;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class BookRepositoryTest {

    @Autowired
    private BookRepository bookRepository;

    @Test
    void savesAndFindsBookByIsbn() {
        bookRepository.save(new Book("Effective Java", "Joshua Bloch", "978-0134685991", 45.0));

        Optional<Book> found = bookRepository.findByIsbn("978-0134685991");

        assertThat(found).isPresent();
        assertThat(found.get().getTitle()).isEqualTo("Effective Java");
        assertThat(found.get().getId()).isNotNull();
    }

    @Test
    void findsBooksByAuthorIgnoringCase() {
        bookRepository.save(new Book("Effective Java", "Joshua Bloch", "978-0134685991", 45.0));
        bookRepository.save(new Book("Java Concurrency in Practice", "Joshua Bloch", "978-0321349606", 50.0));

        List<Book> books = bookRepository.findByAuthorIgnoreCase("joshua bloch");

        assertThat(books).hasSize(2);
    }

    @Test
    void existsByIsbnReturnsTrueForExistingBook() {
        bookRepository.save(new Book("Effective Java", "Joshua Bloch", "978-0134685991", 45.0));

        assertThat(bookRepository.existsByIsbn("978-0134685991")).isTrue();
        assertThat(bookRepository.existsByIsbn("does-not-exist")).isFalse();
    }
}
