package com.trylast.demonew.config;

import com.trylast.demonew.services.UserDetailsServiceImp;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class Springsecurity {
    @Autowired
    UserDetailsServiceImp userDetailsService;

    @Autowired
    private JWTFilter jwtFilter;

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity httpSecurity) throws Exception {
//          return httpSecurity.csrf().disable()
//                  .authorizeHttpRequests(request -> request
//                          .requestMatchers("/api/public/**")
//                          .permitAll()
//                          .anyRequest().authenticated()
////                                  .requestMatchers("/api/journal/**", "/api/user/**")
////                                  .authenticated()
////                                  .requestMatchers("/api/public/**")
////                                  .permitAll()
////                                    .requestMatchers("/api/admin/**").hasRole("ADMIN")
////                                    .anyRequest()
////                                    .permitAll()
//                  )
//                  .httpBasic(Customizer.withDefaults())
//                  .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
//                  .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
//                  .build();
        AuthenticationManagerBuilder authenticationManagerBuilder = httpSecurity.getSharedObject(AuthenticationManagerBuilder.class);
        authenticationManagerBuilder.userDetailsService(userDetailsService).passwordEncoder(bCryptPasswordEncoder());
        AuthenticationManager authenticationManager = authenticationManagerBuilder.build();
        httpSecurity.csrf().disable()
                .authorizeHttpRequests()
                .requestMatchers("/api/journal/**", "/api/user/**").authenticated()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest()
                .permitAll()
                .and()
                .authenticationManager(authenticationManager)
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
                .httpBasic();

        return httpSecurity.build();
    }
}