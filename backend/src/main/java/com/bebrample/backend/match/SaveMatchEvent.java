package com.bebrample.backend.match;

import com.bebrample.backend.entity.RoomState;
import com.bebrample.backend.room.Room;
import com.bebrample.backend.room.ws.dto.MoveDto;
import com.bebrample.backend.user.dto.UserLobbyDto;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@AllArgsConstructor
public class SaveMatchEvent {
    private Room room;
    private List<MoveDto> moves;
    private UserLobbyDto winner;
    private RoomState state;
}
