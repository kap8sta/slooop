package com.bebrample.backend.chess;

import com.bebrample.backend.common.exception.RoomException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestClient;

@Service
@Slf4j
@RequiredArgsConstructor
public class ChessService {
    private final RestClient restClient;

    public MakeMoveResponseDto makeMove(String fen, String move) {
        log.debug("FEN: {}, MOVE: {}", fen, move);
        try {
            return restClient.post()
                    .uri("/api/v1/chess/make-move")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(new MakeMoveRequestDto(fen, move))
                    .retrieve()
                    .body(MakeMoveResponseDto.class);
        } catch (HttpClientErrorException.BadRequest exception) {
            throw new RoomException("Probably illegal move");
        } catch (HttpServerErrorException.InternalServerError e) {
            throw new RuntimeException("Internal server error");
        }
    }
}
