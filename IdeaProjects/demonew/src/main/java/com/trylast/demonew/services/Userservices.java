package com.trylast.demonew.services;

import com.trylast.demonew.entity.Userentry;
import com.trylast.demonew.mongodbrepo.Userrepo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
public class Userservices {

    @Autowired
    private Userrepo userrepo;

    @Autowired
    private JWTServices jwtServices;

    @Autowired
    private AuthenticationManager authenticationManager;

    private BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public List<Userentry> getalluser(){
        return userrepo.findAll();
    }

    public Userentry addnewentry(Userentry newuser, boolean passwordencoded){
        if(!passwordencoded) {
            newuser.setPassword(encoder.encode(newuser.getPassword()));
        }
        newuser.setRoles(Arrays.asList("USER"));
//        List<String> roles = newuser.getRoles();
//        if(!roles.contains("USER")){
//            roles.add("USER");
//            newuser.setRoles(roles);
//        }
        userrepo.save(newuser);
        return newuser;
    }

    public Userentry addnewadminentry(Userentry newuser, boolean passwordencoded){
        if(!passwordencoded) {
            newuser.setPassword(encoder.encode(newuser.getPassword()));
        }
        newuser.setRoles(Arrays.asList("USER", "ADMIN"));
        userrepo.save(newuser);
        return newuser;
    }

    public Userentry findByUserName(String username){
        return userrepo.findByUserName(username);
    }

    public void deleteByUserName(String username){ userrepo.deleteByUserName(username);}

    public String verifyuser(Userentry user) {
        Authentication authentication = authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(user.getUserName(), user.getPassword()));

        if(authentication.isAuthenticated()){
            return jwtServices.generatejwttoken(user.getUserName());
        }
        return "fail";
    }
}

