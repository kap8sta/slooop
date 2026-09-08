package com.bebrample.backend.match;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface MatchRepository extends JpaRepository<Match, Long> {
    @Query("select m from Match m " +
            "left join fetch m.blackPlayer m1 " +
            "left join fetch m.whitePlayer m2 " +
            "where m1.id=:id OR m2.id=:id")
    List<Match> findMatchesByPlayerId(@Param("id") Long id);

    @Query("select m from Match m " +
            "left join fetch m.blackPlayer " +
            "left join fetch m.whitePlayer")
    List<Match> findAll();

    @Query("select m from Match m " +
            "left join fetch m.whitePlayer " +
            "left join fetch m.blackPlayer " +
            "where m.id = :id")
    Optional<Match> findById(@Param("id") Long id);
}
