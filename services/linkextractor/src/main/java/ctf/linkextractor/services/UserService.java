package ctf.linkextractor.services;

import ctf.linkextractor.DB;
import ctf.linkextractor.Hasher;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;
import org.apache.commons.codec.binary.Base64;

import java.io.*;

public class UserService {

    public static UserService singletone = new UserService();

    public User RegisterOrLoginUser(UserRegisterModel model){
        User user = DB.registerUser(model);
        if(user != null)
            return user;

        user = DB.findUserByLogin(model.getLogin());
        if(user == null)
            return null;

        if(ValidatePassword(user, model.getPassword()))
            return user;

        //TODO or throw unauthorized exception?
        return null;
    }

    private boolean ValidatePassword(User user, String passwordToCheck){
        String hash = user.getPasswordHash();
        String hashToCheck = Hasher.singletone.calculateHMAC(passwordToCheck);

        //TODO or more time-based-attcaks safe checking?
        return hashToCheck.compareTo(hash) == 0;
    }

    public boolean ValidateUser(User user){
        String hash = user.getPasswordHash();
        if(hash == null)
            return false;

        User existingUser = DB.findUserByLogin(user.getLogin());
        if(existingUser == null)
            return false;

        return hash.compareTo(existingUser.getPasswordHash()) == 0;
    }

    public User parseUserCookie(String cookieValue){
        if(cookieValue == null || cookieValue.isEmpty())
            return null;
        byte[] serialized = Base64.decodeBase64(cookieValue);
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(serialized);
        ObjectInputStream objectInputStream = null;

        try {
            //TODO use classloader to protect from deserialization vulnerabilities ^_^
            objectInputStream = new ObjectInputStream(byteArrayInputStream);
            return (User)objectInputStream.readObject();
        } catch (Exception e) {
            return null;
        }
        finally {
            try {
                if(objectInputStream != null)
                    objectInputStream.close();
                byteArrayInputStream.close();
            } catch (IOException e) {
            }
        }
    }

    public String createUserCookie(User user){
        if(user == null)
            return null;
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        ObjectOutputStream objectOutputStream = null;

        try {
            objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);
            objectOutputStream.writeObject(user);
            objectOutputStream.flush();
            return Base64.encodeBase64String(byteArrayOutputStream.toByteArray());
        } catch (IOException e) {
            return null;
        } finally {
            try {
                if(objectOutputStream != null)
                    objectOutputStream.close();
                byteArrayOutputStream.close();
            }catch (IOException ex){
            }
        }
    }
}
