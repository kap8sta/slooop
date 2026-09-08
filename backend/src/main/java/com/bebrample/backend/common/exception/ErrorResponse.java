package com.bebrample.backend.common.exception;

import lombok.*;
import org.hibernate.validator.constraints.Normalized;

import java.time.LocalDateTime;
@Getter
@Setter
@NoArgsConstructor
public class ErrorResponse {
    private LocalDateTime timestamp = LocalDateTime.now();
    private int status;
    private String error;
    private String message;

    public ErrorResponse(int status, String error, String message) {
        this.status = status;
        this.error = error;
        this.message = message;
    }
}
