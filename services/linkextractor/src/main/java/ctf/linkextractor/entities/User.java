package ctf.linkextractor.entities;


import ctf.linkextractor.Hasher;

import java.io.Serializable;

public class User implements Serializable {

    private String login;
    private String passwordHash;

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
