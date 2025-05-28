package com.trylast.demonew.controller;

import com.trylast.demonew.entity.Userentry;
import com.trylast.demonew.services.Userservices;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/public")
@Slf4j
public class Publicuser {

    @Autowired
    private Userservices userservices;

    @GetMapping
    public String healthcheck(){
        log.info("Info Logging is wokring");
        log.debug("Debug Logging is wokring");
        return "Logging is wokring";
    }

    @PostMapping("/login")
    public String loginrequest(@RequestBody Userentry user){
        return userservices.verifyuser(user);
    }

    @PostMapping
    public ResponseEntity<Userentry> addentry(@RequestBody Userentry newuser){
        try{
            userservices.addnewentry(newuser, false);
            return new ResponseEntity<>(newuser, HttpStatus.CREATED);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }
}
