package com.trylast.demonew.controller;

import com.trylast.demonew.entity.*;
import com.trylast.demonew.services.Journalservices;
import com.trylast.demonew.services.Userservices;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.Dictionary;
import java.util.Hashtable;
import java.util.List;

@RestController
@RequestMapping("/api/journal")
public class Journalentrycontroller {

    @Autowired
    private Journalservices journalservices;

    @Autowired
    private Userservices userservices;

//    @GetMapping
//    public ResponseEntity<?> getalljournals(){
//        List<Journalentry> all = journalservices.getallentries();
//        if(all != null && !all.isEmpty()){
//            return new ResponseEntity<>(all, HttpStatus.OK);
//        }
//        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
//    }

    @GetMapping
    public ResponseEntity<?> getalljournalsforuser(){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        Userentry user = userservices.findByUserName(username);
        if(user != null){
            List<Journalentry> all = user.getJournalentries();
            if(all != null && !all.isEmpty()) {
                return new ResponseEntity<>(all, HttpStatus.OK);
            }
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @PostMapping
    public ResponseEntity<Journalentry> addentryforuser(@RequestBody Journalentry newentry){
        try{
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String username = authentication.getName();
            Userentry olduser = userservices.findByUserName(username);
            if(olduser != null) {
                journalservices.addnewentry(newentry, username);
                return new ResponseEntity<>(newentry, HttpStatus.CREATED);
            }
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        } catch (Exception e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }

    }

    @GetMapping("/id/{getid}")
    public ResponseEntity<Journalentry> getjournalbyid(@PathVariable String getid){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        Userentry olduser = userservices.findByUserName(username);
        List<Journalentry> jlist = olduser.getJournalentries();

        for(int i=0;i<jlist.size();i++){
            if(jlist.get(i).getId().equals(getid)){
                Journalentry entry = journalservices.findById(getid).orElse(null);
                if(entry != null){
                    return new ResponseEntity<>(entry, HttpStatus.OK);
                }
            }
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @DeleteMapping("/id/{deleteid}")
    public ResponseEntity<?> deleteentry(@PathVariable String deleteid){
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        boolean removed = journalservices.deleteentry(deleteid, username);
        Dictionary<String, String> response = new Hashtable<>();
        response.put("status", "Journal Entery deleted successfully!!!");
        if(removed){
            return new ResponseEntity<>(response, HttpStatus.OK);
        }
        else{
            response.put("status", "Journal Entery not found!!!");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }
    }

    @PutMapping("/id/{updateid}")
    public ResponseEntity<Journalentry> updateentry(@PathVariable String updateid, @RequestBody Journalentry updateentry){
        Journalentry oldentry = journalservices.findById(updateid).orElse(null);
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        Userentry olduser = userservices.findByUserName(username);
        List<Journalentry> jlist = olduser.getJournalentries();

        for(int i=0;i<jlist.size();i++){
            if(jlist.get(i).getId().equals(updateid)){
                if(oldentry != null){
                    oldentry.setStatus(updateentry.getStatus() != null && !updateentry.getStatus().equals("") ? updateentry.getStatus() : oldentry.getStatus());
                    oldentry.setTitle(updateentry.getTitle() != null && !updateentry.getTitle().equals("") ? updateentry.getTitle() : oldentry.getTitle());
                    journalservices.addnewentry(oldentry, username);
                    return new ResponseEntity<>(oldentry, HttpStatus.OK);
                }
            }
        }
        return new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
