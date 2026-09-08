package com.bebrample.backend.match;

import com.bebrample.backend.common.exception.ResourcesNotFoundException;
import com.bebrample.backend.entity.Color;
import com.bebrample.backend.entity.RoomState;
import com.bebrample.backend.match.dto.MatchResponseDto;
import com.bebrample.backend.room.Room;
import com.bebrample.backend.room.ws.dto.MoveDto;
import com.bebrample.backend.user.UserRepository;
import com.bebrample.backend.user.dto.UserLobbyDto;
import com.bebrample.backend.user.entity.User;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MatchService {

    private final UserRepository userRepository;
    private final MatchRepository matchRepository;
    @Transactional
    public void saveMatch(Room room, List<MoveDto> moves, UserLobbyDto winner, RoomState state){
        Long whitePlayerId = (room.getFirstPlayer().getColor().equals(Color.WHITE)
                ? room.getFirstPlayer().getId() : room.getSecondPlayer().getId());
        Long blackPlayerId = (Objects.equals(whitePlayerId, room.getFirstPlayer().getId()))
                ? room.getSecondPlayer().getId() : room.getFirstPlayer().getId();


        Match match = new Match();
        match.setRoomUuid(room.getUuid());
        User whitePlayer = userRepository.findUserById(whitePlayerId)
                .orElseThrow(() -> new ResourcesNotFoundException("User not found in db"));
        User blackPlayer = userRepository.findUserById(blackPlayerId)
                .orElseThrow(() -> new ResourcesNotFoundException("User not found in db"));
        match.setBlackPlayer(blackPlayer);
        match.setWhitePlayer(whitePlayer);
        match.setFinalFen(room.getCurrentFen());
        match.setResultBasedOnPlayer(winner.getColor(), state);
        match.setPgn(generatePgn(moves));
        matchRepository.save(match);
    }

    private String generatePgn(List<MoveDto> moves){
        return moves.stream()
                .map(move -> move.getFrom() + "-" + move.getTo())
                .collect(Collectors.joining(" "));
    }

    public List<MatchResponseDto> getPlayerMatches(Long id){
        List<Match> matches = matchRepository.findMatchesByPlayerId(id);
        List<MatchResponseDto> matchDtos = new ArrayList<>();
        for(Match m : matches){
            MatchResponseDto dto = matchToMatchResponseDto(m);
            matchDtos.add(dto);
        }
        return matchDtos;
    }
    public MatchResponseDto getMatch(Long id){
        Match m = matchRepository.findById(id).orElseThrow(() -> new ResourcesNotFoundException("not found"));
        return matchToMatchResponseDto(m);
    }

    private UserLobbyDto userToUserLobbyDto(User player, Color color){
        Color colorToSet = (color == Color.WHITE) ? Color.WHITE : Color.BLACK;
        return new UserLobbyDto(player.getId(), player.getUsername(), colorToSet);
    }
    private MatchResponseDto matchToMatchResponseDto(Match m){
        return new MatchResponseDto(m.getId(),
                m.getRoomUuid(),
                userToUserLobbyDto(m.getWhitePlayer(), Color.WHITE),
                userToUserLobbyDto(m.getBlackPlayer(), Color.BLACK),
                m.getFinalFen(),
                m.getPgn(),
                m.getResult());
    }

    public List<MatchResponseDto> getAllMatches() {
        List<Match> matches = matchRepository.findAll();
        List<MatchResponseDto> matchDtos = new ArrayList<>();
        for(Match m : matches){
            MatchResponseDto dto = matchToMatchResponseDto(m);
            matchDtos.add(dto);
        }
        return matchDtos;
    }
}
