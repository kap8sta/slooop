package com.bebrample.backend.room;

import com.bebrample.backend.chess.ChessService;
import com.bebrample.backend.chess.MakeMoveResponseDto;
import com.bebrample.backend.common.exception.ResourcesNotFoundException;
import com.bebrample.backend.common.exception.RoomException;
import com.bebrample.backend.entity.Color;
import com.bebrample.backend.entity.RoomState;
import com.bebrample.backend.match.SaveMatchEvent;
import com.bebrample.backend.room.ws.dto.GameOverDto;
import com.bebrample.backend.room.ws.dto.MoveDto;
import com.bebrample.backend.room.ws.dto.WebSocketEvent;
import com.bebrample.backend.user.dto.UserLobbyDto;
import com.bebrample.backend.user.entity.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;
import java.util.concurrent.ThreadLocalRandom;

@Service
@Slf4j
@RequiredArgsConstructor
public class RoomService {
    private final LobbyParticipantMapper lobbyParticipantMapper;
    private final RedisRepository redisRepository;
    private final SimpMessagingTemplate simpMessagingTemplate;
    private final ApplicationEventPublisher eventPublisher;
    private final ChessService chessService;

        public Room createRoom(LobbyParticipant participant){



            if(redisRepository.isPlaying(participant.getId())) throw new RoomException("You already playing!");

            UserLobbyDto dto = lobbyParticipantMapper.toUserLobbyDto(participant);
            Room room = new Room();
            room.setFirstPlayer(dto);
            room.setSecondPlayer(null);
            room.setRoomState(RoomState.WAITING_FOR_OPPONENT);

            redisRepository.saveOrUpdateUser(room.getUuid(), participant.getId());
            redisRepository.saveOrUpdateRoom(room);
            sendUpdateMessage(room);
            return room;
        }
        public Room connectToRoom(String roomUuid, LobbyParticipant user){
            Room room = redisRepository.getRoom(roomUuid);
            if (room == null) throw new ResourcesNotFoundException("Room is null");
            if(redisRepository.isPlaying(user.getId()) || Objects.equals(room.getFirstPlayer().getId(), user.getId())) {
                throw new RoomException("User already playing this or other game");
            }
            if(room.getSecondPlayer() != null) throw new RoomException("Room is already full");
            UserLobbyDto dto = lobbyParticipantMapper.toUserLobbyDto(user);
            room.setSecondPlayer(dto);
            startGame(room);
            log.info("{} <- second player", room.getSecondPlayer());

            redisRepository.saveOrUpdateRoom(room);
            redisRepository.saveOrUpdateUser(room.getUuid(), user.getId());
            sendUpdateMessage(room);
            return room;
        }

        public void updateChessState(String roomUuid, MoveDto move, LobbyParticipant user){
            Room room = redisRepository.getRoom(roomUuid);
            if(room == null) throw new ResourcesNotFoundException("Room is null");
            if(room.getRoomState() != RoomState.ONGOING && room.getRoomState() != RoomState.CHECK) throw new RoomException("Game is finished. its over.");

            UserLobbyDto whoMadeMove = null;
            Color atStart = room.getActiveColor();

            String redisRoomUuid = redisRepository.getUserRoomUuid(user.getId());
            if(!roomUuid.equals(redisRoomUuid)) throw new RoomException("You are not playing this game");

            if(user.getId().equals(room.getFirstPlayer().getId())) whoMadeMove = room.getFirstPlayer();
             else if(user.getId().equals(room.getSecondPlayer().getId())) whoMadeMove = room.getSecondPlayer();

            if(whoMadeMove == null) throw new ResourcesNotFoundException("Player somehow not authorized");
            if(whoMadeMove.getColor() != room.getActiveColor()) throw new RoomException("Not your move");

            String fen = room.getCurrentFen();
            String uci = move.getFrom() + move.getTo();
            if (move.getPromotion() != null && !move.getPromotion().isBlank()) {
                uci += move.getPromotion().toLowerCase();
            }
            MakeMoveResponseDto responseMove = chessService.makeMove(fen, uci);
            log.info(String.valueOf(responseMove));
            room.setCurrentFen(responseMove.getFen());
            simpMessagingTemplate.convertAndSend("/topic/rooms/" + roomUuid, new WebSocketEvent<>("MOVE", responseMove));
            sendUpdateMessage(room);
            redisRepository.addMoveList(roomUuid, move);
            List<MoveDto> moves = redisRepository.getMoves(roomUuid);
            simpMessagingTemplate.convertAndSend("/topic/rooms/" + roomUuid, new WebSocketEvent<>("MATCH_MOVES", moves));
//            if(responseMove.getIsCheckmate() || responseMove.getIsStalemate()){
//                endGame(roomUuid, whoMadeMove);
//                return;
//            }
                switch (responseMove.getGameStatus()) {
                    case "checkmate" -> {
                        room.setRoomState(RoomState.CHECKMATE);
                        endGame(room, whoMadeMove);
                        return;
                    }
                    case "stalemate" -> {
                        room.setRoomState(RoomState.STALEMATE);
                        endGame(room, whoMadeMove);
                        return;
                    }
                    case "draw" -> {
                        room.setRoomState(RoomState.DRAW);
                        endGame(room, whoMadeMove);
                        return;
                    }
            }
            room.setActiveColor(atStart.toggle());
            redisRepository.saveOrUpdateRoom(room);
        }

        private void endGame(Room room, UserLobbyDto whoMadeMove){
            sendUpdateMessage(room);
            GameOverDto gameOverDto = new GameOverDto(whoMadeMove.getUsername(), room.getRoomState());
            simpMessagingTemplate.convertAndSend("/topic/rooms/" + room.getUuid(),
                    new WebSocketEvent<>("GAME_OVER", gameOverDto));

            boolean bothRegistered = room.getSecondPlayer() != null
                    && room.getSecondPlayer().getId() > 0
                    && room.getFirstPlayer().getId() > 0;
            if (!bothRegistered) {
                log.info("game played with guest/not full lobby. prevent from saving");
                redisRepository.clearMatchData(room);
                return;
            }
            List<MoveDto> moves = redisRepository.getMoves(room.getUuid());
            SaveMatchEvent event = new SaveMatchEvent(room, moves, whoMadeMove, room.getRoomState());
            eventPublisher.publishEvent(event);
            log.info("saved game with room id:{}", room.getUuid());
            redisRepository.clearMatchData(room);
        }



        private void randomizeSides(Room room){
            boolean rng = ThreadLocalRandom.current().nextBoolean();
            if(rng){
                room.getFirstPlayer().setColor(Color.WHITE);
                room.getSecondPlayer().setColor(Color.BLACK);
            } else {
                room.getFirstPlayer().setColor(Color.BLACK);
                room.getSecondPlayer().setColor(Color.WHITE);
            }
        }

        private void startGame(Room room){
            //TODO: refactor to use python service for start game
            randomizeSides(room);
            room.setRoomState(RoomState.ONGOING);
            room.setCurrentFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
            room.setActiveColor(Color.WHITE);
        }

        private void sendUpdateMessage(Room room){
            simpMessagingTemplate.convertAndSend("/topic/rooms/" + room.getUuid(), new WebSocketEvent<>("ROOM_INFO", room ));
        }

        public List<Room> findAllRooms(){
            return redisRepository.getAllRooms();
        }
        public List<String> findAllPlayingUsers(){
            return redisRepository.getAllPlayingUsers();
        }

}
