package com.bebrample.backend.room.ws.dto;

import lombok.*;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@ToString
public class MoveDto {
    String from;
    String to;
    String promotion;
}
