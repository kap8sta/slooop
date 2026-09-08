package com.bebrample.backend.user;

import com.bebrample.backend.common.exception.ResourcesNotFoundException;
import com.bebrample.backend.common.security.JwtService;
import com.bebrample.backend.user.dto.UserCreateDto;
import com.bebrample.backend.user.dto.UserResponseDto;
import com.bebrample.backend.user.entity.Guest;
import com.bebrample.backend.user.entity.User;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    private final UserRepository userRepository;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    @Transactional
    public UserResponseDto register(UserCreateDto dto){
        Optional<User> userInDb = userRepository.findUserByUsername(dto.getUsername());
        if(userInDb.isPresent()){
            throw new ResourcesNotFoundException("User with current username in database");
        }
        User user = new User();
        user.setUsername(dto.getUsername());
        String password = passwordEncoder.encode(dto.getPassword());
        user.setPassword(password);

        userRepository.save(user);
        return userMapper.toUserResponse(user);
    }
    public String login(UserCreateDto dto){
        User user = userRepository.findUserByUsername(dto.getUsername())
                .orElseThrow(() -> new ResourcesNotFoundException("User not found"));

        if(!passwordEncoder.matches(dto.getPassword(), user.getPassword())){
            throw new ResourcesNotFoundException("Wrong Password");
        }
        return jwtService.generateToken(user.getId().toString(),user.getUsername(), "ROLE_USER");
    }

    public String createGuest(){
        Guest guest = new Guest();
        return jwtService.generateToken(guest.getId().toString(),guest.getUsername(), "ROLE_GUEST");
    }

    public UserResponseDto findById(Long id){
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourcesNotFoundException("User not found"));
        return userMapper.toUserResponse(user);
    }

    public UserResponseDto findByName(String name){
        User user = userRepository.findUserByUsername(name)
                .orElseThrow( () -> new ResourcesNotFoundException("User not found"));
        return userMapper.toUserResponse(user);
    }


    public List<UserResponseDto> findAll() {
        List<User> users = userRepository.findAll();
        return users.stream().map(userMapper::toUserResponse).toList();
    }
}
