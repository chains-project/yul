package com.example.boilerplatefree.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.time.Instant;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@ToString(exclude = "passwordHash")
@EqualsAndHashCode(of = "id")
public class User {

    private Long id;
    private String username;
    private String email;
    private String passwordHash;
    private List<String> roles;
    private Instant createdAt;

    public boolean isAdmin() {
        return roles != null && roles.contains("ADMIN");
    }
}
