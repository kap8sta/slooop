package com.bebrample.backend.room;

import com.bebrample.backend.room.ws.dto.MessageDto;
import com.bebrample.backend.room.ws.dto.MoveDto;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.util.*;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class RedisRepository {
    private final RedisTemplate<String,Room> redisRoomTemplate;
    private final RedisTemplate<String,String> stringRedisTemplate;
    private final RedisTemplate<String, MoveDto> redisMoveDtoTemplate;
    private final RedisTemplate<String, MessageDto> redisMessageTemplate;

    private static final String CACHE_ROOM_KEY_PREFIX = "room:state:";
    private static final String CACHE_MOVES_KEY_PREFIX = "room:moves:";
    private static final String CACHE_PARTICIPANT_KEY_PREFIX = "user:";
    private static final String CACHE_MESSAGES_KEY_PREFIX = "room:messages:";
    private static final String CACHE_ALL_USERS_KEY_PREFIX = "all_users";
    private static final String CACHE_ALL_ROOMS_KEY_PREFIX = "all_rooms";

    public void saveOrUpdateUser(String roomUuid, Long participantId){
        String key = CACHE_PARTICIPANT_KEY_PREFIX + participantId;
        Boolean exists = stringRedisTemplate.hasKey(key);
        stringRedisTemplate.opsForValue()
                .set(key, roomUuid, Duration.ofHours(1));
        if(Boolean.FALSE.equals(exists)){
            stringRedisTemplate.opsForSet().add(CACHE_ALL_USERS_KEY_PREFIX, key);
        }
    }

    public String getUserRoomUuid(Long userId){
        return stringRedisTemplate.opsForValue()
                .get(CACHE_PARTICIPANT_KEY_PREFIX + userId);
    }

    public void deleteUser(Long userId){
        String key = CACHE_PARTICIPANT_KEY_PREFIX + userId;
        stringRedisTemplate.delete(key);
        stringRedisTemplate.opsForSet().remove(CACHE_ALL_USERS_KEY_PREFIX, key);
    }
    public void deleteRoom(Room room) {
        String key = CACHE_ROOM_KEY_PREFIX + room.getUuid();
        redisRoomTemplate.delete(key);
        stringRedisTemplate.opsForSet().remove(CACHE_ALL_ROOMS_KEY_PREFIX, key);
    }

    public void deleteMoves(Room room) {
        redisMoveDtoTemplate.delete(CACHE_MOVES_KEY_PREFIX + room.getUuid());
    }

    public List<MoveDto> getMoves(String roomUuid){
        return redisMoveDtoTemplate.opsForList().range(CACHE_MOVES_KEY_PREFIX + roomUuid, 0, -1);
    }

    public boolean isPlaying(Long userId){
        String player = stringRedisTemplate.opsForValue()
                .get(CACHE_PARTICIPANT_KEY_PREFIX + userId);
        return player != null;
    }

    public Room getRoom(String roomUuid){
            return redisRoomTemplate.opsForValue()
                    .get(CACHE_ROOM_KEY_PREFIX + roomUuid);
    }

    public void saveOrUpdateRoom(Room room){
        String key = CACHE_ROOM_KEY_PREFIX + room.getUuid();
        Boolean exists = redisRoomTemplate.hasKey(key);
        redisRoomTemplate.opsForValue()
                .set(key, room, Duration.ofHours(1));

        if(Boolean.FALSE.equals(exists)) stringRedisTemplate.opsForSet().add(CACHE_ALL_ROOMS_KEY_PREFIX, key);
    }

    public List<Room> getAllRooms(){
        Set<String> keys = stringRedisTemplate.opsForSet().members(CACHE_ALL_ROOMS_KEY_PREFIX);
        if(keys == null) return Collections.emptyList();
        List<Room> rooms = redisRoomTemplate.opsForValue().multiGet(keys);
        List<Room> existingRoomsList = rooms.stream().filter(Objects::nonNull).collect(Collectors.toList());

        Set<String> liveKeys = existingRoomsList.stream()
                .map(Room::getUuid)
                .collect(Collectors.toSet());

        Set<String> staleKeys = new HashSet<>(keys);
        staleKeys.removeAll(liveKeys);

        if (!staleKeys.isEmpty())
            stringRedisTemplate.opsForSet().remove(
                    CACHE_ALL_ROOMS_KEY_PREFIX, staleKeys.toArray(new Object[0]));

        return existingRoomsList;
    }

    public List<String> getAllPlayingUsers() {
        Set<String> keys = stringRedisTemplate.opsForSet().members(CACHE_ALL_USERS_KEY_PREFIX);
        if (keys == null || keys.isEmpty()) return Collections.emptyList();

        List<String> keyList = new ArrayList<>(keys);
        List<String> userValues = stringRedisTemplate.opsForValue().multiGet(keyList);
        if (userValues == null) return Collections.emptyList();

        List<String> existingUsers = new ArrayList<>();
        List<String> staleKeys = new ArrayList<>();

        for (int i = 0; i < keyList.size(); i++) {
            String user = userValues.get(i);
            if (user != null) existingUsers.add(user);
             else staleKeys.add(keyList.get(i));
        }
        if (!staleKeys.isEmpty()) {
            stringRedisTemplate.opsForSet().remove(
                    CACHE_ALL_USERS_KEY_PREFIX,
                    staleKeys.toArray(new Object[0]));
        }
        return existingUsers;
    }

    public void addMoveList(String roomUuid, MoveDto move){
        redisMoveDtoTemplate.opsForList().rightPush(CACHE_MOVES_KEY_PREFIX + roomUuid, move);
        redisMoveDtoTemplate.expire(CACHE_MOVES_KEY_PREFIX + roomUuid, Duration.ofHours(1));
    }



    public void clearMatchData(Room room){
        deleteUser(room.getFirstPlayer().getId());
        deleteUser(room.getSecondPlayer().getId());
        deleteRoom(room);
        deleteMoves(room);
        deleteMessages(room.getUuid());
    }

    public void saveMessage(String roomUuid, MessageDto message){
        redisMessageTemplate.opsForList().rightPush(CACHE_MESSAGES_KEY_PREFIX + roomUuid, message);
        redisMessageTemplate.expire(CACHE_MESSAGES_KEY_PREFIX + roomUuid, Duration.ofHours(1));
    }

    public List<MessageDto> getMessages(String roomUuid) {
        return redisMessageTemplate.opsForList().range(CACHE_MESSAGES_KEY_PREFIX + roomUuid, 0, -1);
    }

    public void deleteMessages(String roomUuid){
        redisMessageTemplate.delete(CACHE_MESSAGES_KEY_PREFIX + roomUuid);
    }
}
