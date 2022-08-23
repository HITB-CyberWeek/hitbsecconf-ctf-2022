package ctf.linkextractor.entities;


import ctf.linkextractor.Hasher;

import java.io.Serializable;
import java.util.HashSet;
import java.util.List;

public class User implements Serializable {

    private String login;
    private String passwordHash;

    public HashSet<Page> pages;
    public void setPages(List<Page> p){
        pages = new HashSet<>(p);
    }

    public String getLogin() {
        return login;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public User(String login, String password) {
        this.login = login;
        this.passwordHash = Hasher.singletone.calculateHMAC(password);
    }
}
