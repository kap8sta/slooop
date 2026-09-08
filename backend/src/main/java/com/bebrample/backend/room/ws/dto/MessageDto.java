package com.bebrample.backend.room.ws.dto;


import lombok.Getter;

import java.time.Instant;
@Getter
public class MessageDto {
    Instant time = Instant.now();
    String message;
    String username;

    public MessageDto(String message, String username){
        this.message = message;
        this.username = username;
    }
}
