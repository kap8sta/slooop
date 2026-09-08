package com.bebrample.backend.user.entity;

public interface LobbyParticipant {

    Long getId();
    boolean isGuest();
    String getUsername();
}
