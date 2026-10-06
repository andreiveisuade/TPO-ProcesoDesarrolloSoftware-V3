package com.uade.tpejemplo.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.JwtParser;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import com.uade.tpejemplo.service.TokenService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.Optional;
import java.util.function.Function;

// Genera y valida los JWT de la sesion.
// Adapter: implementa TokenService (Target) y delega en JwtParser/SecretKey de jjwt (Adaptee, por composicion)
@Component
public class JwtUtil implements TokenService {

    private final SecretKey key;
    private final JwtParser parser;
    private final long expirationMs;

    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration-ms}") long expirationMs) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes());
        this.parser = Jwts.parser().verifyWith(key).build();
        this.expirationMs = expirationMs;
    }

    @Override
    public String generarToken(String username) {
        return Jwts.builder()
            .subject(username)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expirationMs))
            .signWith(key)
            .compact();
    }

    @Override
    public Optional<String> extraerUsername(String token) {
        try {
            return Optional.ofNullable(extraerClaim(token, Claims::getSubject));
        } catch (JwtException | IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    @Override
    public boolean esValido(String token, String username) {
        return extraerUsername(token).filter(username::equals).isPresent();
    }

    private <T> T extraerClaim(String token, Function<Claims, T> resolver) {
        Claims claims = parser
            .parseSignedClaims(token)
            .getPayload();
        return resolver.apply(claims);
    }
}
