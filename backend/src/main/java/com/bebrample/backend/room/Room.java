package com.bebrample.backend.room;

import com.bebrample.backend.entity.Color;
import com.bebrample.backend.entity.RoomState;
import com.bebrample.backend.user.dto.UserLobbyDto;
import lombok.*;

import java.util.Map;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class Room {
    private String uuid = UUID.randomUUID().toString();
    private RoomState roomState;
    private UserLobbyDto firstPlayer;
    private UserLobbyDto secondPlayer;
    private String currentFen;
    private Color activeColor;
    private Map<String, String[]> legal_moves;
}
