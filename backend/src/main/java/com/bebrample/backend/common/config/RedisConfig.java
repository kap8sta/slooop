package com.bebrample.backend.common.config;

import com.bebrample.backend.match.Match;
import com.bebrample.backend.room.Room;
import com.bebrample.backend.room.ws.dto.MessageDto;
import com.bebrample.backend.room.ws.dto.MoveDto;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.JacksonJsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;
import tools.jackson.databind.ObjectMapper;


@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Match> redisMatchTemplate(RedisConnectionFactory redisConnectionFactory, ObjectMapper objectMapper){
        RedisTemplate<String, Match> template = new RedisTemplate<>();

        template.setConnectionFactory(redisConnectionFactory);

        RedisSerializer<String> serializer = RedisSerializer.string();
        JacksonJsonRedisSerializer<Match> jsonSerializer = new JacksonJsonRedisSerializer<>(objectMapper, Match.class);
        template.setKeySerializer(serializer);
        template.setValueSerializer(serializer);
        template.setHashKeySerializer(serializer);
        template.setHashValueSerializer(jsonSerializer);
        return template;
    }
    @Bean
    public RedisTemplate<String, Room> redisRoomTemplate(RedisConnectionFactory redisConnectionFactory, ObjectMapper objectMapper){
        RedisTemplate<String, Room> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);

        RedisSerializer<String> serializer = new StringRedisSerializer();
        JacksonJsonRedisSerializer<Room> jsonSerializer = new JacksonJsonRedisSerializer<>(objectMapper,Room.class);
        template.setKeySerializer(serializer);
        template.setValueSerializer(jsonSerializer);
        template.afterPropertiesSet();
        return template;
    }
    @Bean
    public RedisTemplate<String, String> redisStringTemplate(RedisConnectionFactory redisConnectionFactory, ObjectMapper objectMapper){
        RedisTemplate<String, String> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);

        RedisSerializer<String> serializer = new StringRedisSerializer();
        //JacksonJsonRedisSerializer<LobbyParticipant> jsonSerializer = new JacksonJsonRedisSerializer<>(objectMapper,LobbyParticipant.class);
        template.setKeySerializer(serializer);
        template.setValueSerializer(serializer);
        template.afterPropertiesSet();
        return template;
    }
    @Bean
    public RedisTemplate<String, MoveDto> redisMoveTemplate(RedisConnectionFactory redisConnectionFactory, ObjectMapper objectMapper) {
        RedisTemplate<String, MoveDto> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);

        RedisSerializer<String> serializer = new StringRedisSerializer();
        JacksonJsonRedisSerializer<MoveDto> jsonSerializer = new JacksonJsonRedisSerializer<>(objectMapper, MoveDto.class);
        template.setKeySerializer(serializer);
        template.setValueSerializer(jsonSerializer);
        template.afterPropertiesSet();
        return template;
    }
    @Bean
    public RedisTemplate<String, MessageDto> redisMessageTemplate(RedisConnectionFactory redisConnectionFactory, ObjectMapper objectMapper) {
        RedisTemplate<String, MessageDto> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);

        RedisSerializer<String> serializer = new StringRedisSerializer();
        JacksonJsonRedisSerializer<MessageDto> jsonSerializer = new JacksonJsonRedisSerializer<>(objectMapper, MessageDto.class);
        template.setKeySerializer(serializer);
        template.setValueSerializer(jsonSerializer);
        template.afterPropertiesSet();
        return template;
    }

}