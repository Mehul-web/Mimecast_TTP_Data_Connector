package com.trylast.demonew.mongodbrepo;

import com.trylast.demonew.entity.Journalentry;
import org.springframework.data.mongodb.repository.MongoRepository;


public interface Mongorepo extends MongoRepository<Journalentry, String> {

}
