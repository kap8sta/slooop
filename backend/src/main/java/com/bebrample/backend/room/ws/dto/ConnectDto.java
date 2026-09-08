package com.bebrample.backend.room.ws.dto;

import com.bebrample.backend.entity.Role;
import com.bebrample.backend.entity.RoomState;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class ConnectDto {
    Role role;
    String playerName;
    RoomState roomState;
}
