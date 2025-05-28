package com.trylast.demonew.controller;

import com.trylast.demonew.entity.Userentry;
import com.trylast.demonew.services.Userservices;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user")
public class Usercontroller {

    @Autowired
    private Userservices userservices;

//    @GetMapping
//    public ResponseEntity<?> getall(){
//        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
//        String username = authentication.getName();
//        Userentry olduser = userservices.findByUserName(username);
//
//        if(olduser == null){
//            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
//        }
//        List<String> roles = olduser.getRoles();
//
//        for(int i=0;i<roles.size();i++){
//            if(roles.get(i).equals("ADMIN")){
//                List<Userentry> all = userservices.getalluser();
//                if(all != null && !all.isEmpty()){
//                    return new ResponseEntity<>(all, HttpStatus.OK);
//                }
//            }
//            else{
//                continue;
//            }
//        }
//        return new ResponseEntity<>(olduser, HttpStatus.OK);
//    }

    @GetMapping
    public ResponseEntity<Userentry> getuserbyusername(){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        Userentry entry = userservices.findByUserName(username);
        if(entry != null){
            return new ResponseEntity<>(entry, HttpStatus.OK);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }


    @PutMapping
    public ResponseEntity<Userentry> updateuser(@RequestBody Userentry user){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        Userentry olduser = userservices.findByUserName(username);

        if(olduser != null){
            olduser.setUserName(user.getUserName());
            olduser.setPassword(user.getPassword());
            olduser.setRoles(user.getRoles());
                userservices.addnewentry(olduser, true);
            return new ResponseEntity<>(olduser, HttpStatus.OK);
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
    @DeleteMapping
    public ResponseEntity<?> deleteentry(){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        userservices.deleteByUserName(username);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
