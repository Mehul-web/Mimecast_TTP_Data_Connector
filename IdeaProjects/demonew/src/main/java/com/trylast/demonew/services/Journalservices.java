package com.trylast.demonew.services;

import com.trylast.demonew.entity.*;
import com.trylast.demonew.mongodbrepo.Mongorepo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Component
public class Journalservices {

    @Autowired
    private Mongorepo mongorepo;
    @Autowired
    private Userservices userservices;

    public List<Journalentry> getallentries(){
        return mongorepo.findAll();
    }

    public Journalentry addnewentry(Journalentry newentry, String username){
        Userentry user = userservices.findByUserName(username);
        Journalentry saved = mongorepo.save(newentry);
        user.getJournalentries().add(saved);
        userservices.addnewentry(user, true);
        return newentry;
    }

    public Journalentry addnewentry(Journalentry newentry){
        mongorepo.save(newentry);
        return newentry;
    }

    public Optional<Journalentry> findById(String id){
         return mongorepo.findById(id);
    }

    @Transactional
    public boolean deleteentry(String id, String username){
        Userentry user = userservices.findByUserName(username);
        boolean removed = user.getJournalentries().removeIf(x -> x.getId().equals(id));
        if(removed) {
            userservices.addnewentry(user, true);
            mongorepo.deleteById(id);
        }
        return removed;
    }
}
