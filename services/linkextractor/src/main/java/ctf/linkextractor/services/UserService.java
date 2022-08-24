package ctf.linkextractor.services;

import ctf.linkextractor.DB;
import ctf.linkextractor.Hasher;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;
import io.javalin.http.UnauthorizedResponse;
import org.apache.commons.codec.binary.Base64;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

public class UserService {

    public static UserService singletone = new UserService();

    public User RegisterOrLoginUser(UserRegisterModel model){
        User user = DB.singletone.registerNewUser(model);
        if(user != null)
            return user;

        user = DB.singletone.findUserByLogin(model.getLogin());
        if(ValidatePassword(user, model.getPassword()))
            return user;

        throw new UnauthorizedResponse("invalid credentials");
    }

    private boolean ValidatePassword(User user, String passwordToCheck){
        String hash = user.getPasswordHash();
        String hashToCheck = Hasher.singletone.calculateHMAC(passwordToCheck);

        return hashToCheck.compareTo(hash) == 0;
    }

    public boolean ValidateUser(User user){
        String hash = user.getPasswordHash();
        if(hash == null)
            return false;

        User existingUser = DB.singletone.findUserByLogin(user.getLogin());
        if(existingUser == null)
            return false;

        return hash.compareTo(existingUser.getPasswordHash()) == 0;
    }

    public User parseUserCookie(String cookieValue){
        if(cookieValue == null || cookieValue.isEmpty())
            return null;

        try (ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(Base64.decodeBase64(cookieValue));
             ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream)) {

            return (User)objectInputStream.readObject();
        } catch (Exception e) {
            return null;
        }
    }

    public String createUserCookie(User user){
        if(user == null)
            return null;

        try (ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
             ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream)) {

            objectOutputStream.writeObject(user);
            objectOutputStream.flush();
            return Base64.encodeBase64String(byteArrayOutputStream.toByteArray());
        } catch (IOException e) {
            return null;
        }
    }
}
