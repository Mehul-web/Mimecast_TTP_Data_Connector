package com.trylast.demonew;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;

@SpringBootApplication
@EnableWebSecurity
public class DemonewApplication {
	public static void main(String[] args) {
		SpringApplication.run(DemonewApplication.class, args);
	}

}
