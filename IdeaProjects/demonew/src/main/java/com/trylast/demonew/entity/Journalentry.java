package com.trylast.demonew.entity;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;


@Document(collection = "journal_entries")
@Data
@NoArgsConstructor
public class Journalentry {

    @Id
    private String id;
    private String title;
    private String status;
}
