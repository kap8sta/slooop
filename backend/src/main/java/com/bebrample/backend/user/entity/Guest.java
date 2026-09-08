package com.bebrample.backend.user.entity;

import lombok.*;

import java.util.concurrent.atomic.AtomicLong;
@AllArgsConstructor
@Getter
@Setter
@Builder
public class Guest implements LobbyParticipant {
    private static final AtomicLong idGenerator = new AtomicLong(-1);
    private Long id;
    private String username;

    public Guest(){
        id = idGenerator.getAndDecrement();
        username = "bebra" + id;
    }
    @Override
    public Long getId() {
        return id;
    }

    @Override
    public boolean isGuest() {
        return true;
    }

    @Override
    public String getUsername() {
        return username;
    }


}
