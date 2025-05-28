package com.trylast.demonew.mongodbrepo;

import com.trylast.demonew.entity.Userentry;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface Userrepo extends MongoRepository<Userentry, String> {
    Userentry findByUserName(String username);
    void deleteByUserName(String username);
}
