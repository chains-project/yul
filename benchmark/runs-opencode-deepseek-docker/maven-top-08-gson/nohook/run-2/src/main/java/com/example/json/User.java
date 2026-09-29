package com.example.json;

import java.time.Instant;
import java.util.List;
import java.util.Objects;

public class User {

    private long id;
    private String name;
    private String email;
    private List<String> roles;
    private Instant createdAt;

    public User() {
    }

    public User(long id, String name, String email, List<String> roles, Instant createdAt) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.roles = roles;
        this.createdAt = createdAt;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public List<String> getRoles() {
        return roles;
    }

    public void setRoles(List<String> roles) {
        this.roles = roles;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof User)) {
            return false;
        }
        User user = (User) o;
        return id == user.id
                && Objects.equals(name, user.name)
                && Objects.equals(email, user.email)
                && Objects.equals(roles, user.roles)
                && Objects.equals(createdAt, user.createdAt);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, email, roles, createdAt);
    }

    @Override
    public String toString() {
        return "User{id=" + id + ", name='" + name + "', email='" + email
                + "', roles=" + roles + ", createdAt=" + createdAt + '}';
    }
}
