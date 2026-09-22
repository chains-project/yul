package com.example.demo.book;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class BookServiceTest {

    @Mock
    private BookRepository bookRepository;

    @InjectMocks
    private BookService bookService;

    @Test
    void createRejectsDuplicateIsbn() {
        Book book = new Book("Effective Java", "Joshua Bloch", "978-0134685991", 45.0);
        when(bookRepository.existsByIsbn("978-0134685991")).thenReturn(true);

        assertThatThrownBy(() -> bookService.create(book))
                .isInstanceOf(DuplicateIsbnException.class);
    }

    @Test
    void findByIdThrowsWhenMissing() {
        when(bookRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> bookService.findById(1L))
                .isInstanceOf(BookNotFoundException.class);
    }

    @Test
    void createSavesBook() {
        Book book = new Book("Effective Java", "Joshua Bloch", "978-0134685991", 45.0);
        when(bookRepository.existsByIsbn("978-0134685991")).thenReturn(false);
        when(bookRepository.save(book)).thenReturn(book);

        assertThat(bookService.create(book)).isSameAs(book);
    }
}
