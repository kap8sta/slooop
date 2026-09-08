package com.bebrample.backend.match.dto;

import com.bebrample.backend.entity.Result;
import com.bebrample.backend.user.dto.UserLobbyDto;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class MatchResponseDto {
    private Long id;
    private String roomUuid;
    private UserLobbyDto whitePlayer;
    private UserLobbyDto blackPlayer;
    private String finalFen;
    private String pgn;
    private Result result;

}
