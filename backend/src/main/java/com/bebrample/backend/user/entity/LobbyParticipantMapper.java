package com.bebrample.backend.user.entity;

import com.bebrample.backend.user.dto.UserLobbyDto;
import org.springframework.stereotype.Component;

@Component
public class LobbyParticipantMapper {

    public UserLobbyDto toUserLobbyDto(LobbyParticipant lobbyParticipant){
        UserLobbyDto dto = new UserLobbyDto();
        dto.setId(lobbyParticipant.getId());
        dto.setUsername(lobbyParticipant.getUsername());
        dto.setColor(null);
        return dto;
    }
}
