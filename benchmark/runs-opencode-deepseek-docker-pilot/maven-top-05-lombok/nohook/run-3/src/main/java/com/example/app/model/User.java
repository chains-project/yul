package com.example.app.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Mutable entity.
 *
 * @Data generates getters, setters, equals, hashCode and toString.
 * Constructors are generated explicitly below.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {

    private Long id;
    private String username;
    private String email;
    private boolean active;
}
