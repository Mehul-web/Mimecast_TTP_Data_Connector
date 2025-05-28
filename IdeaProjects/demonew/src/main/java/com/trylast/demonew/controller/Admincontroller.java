package com.trylast.demonew.controller;
import com.trylast.demonew.entity.Userentry;
import com.trylast.demonew.services.Userservices;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
public class Admincontroller {

    @Autowired
    private Userservices userservices;

    @GetMapping("/all-user")
    public ResponseEntity<?> getallusers(){
        List<Userentry> users = userservices.getalluser();
        if(users != null && !users.isEmpty()){
            return new ResponseEntity<>(users, HttpStatus.OK);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @PostMapping("/create-admin")
    public ResponseEntity<?> createnewadmin(@RequestBody Userentry newadmin){
        try{
            userservices.addnewadminentry(newadmin, false);
            return new ResponseEntity<>(newadmin, HttpStatus.CREATED);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }
}
