package com.bebrample.backend.user.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class UserCreateDto {
    @NotBlank
    @Size(min = 3, max = 20, message = "username must be from 3 to 20 symbols")
    private String username;
    @NotBlank(message = "must not be empty")
    @Size(min = 5, max = 20, message = "password must be from 5 to 20 symbols")
    private String password;
}
