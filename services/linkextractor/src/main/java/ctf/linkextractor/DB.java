package ctf.linkextractor;

import ctf.linkextractor.entities.Link;
import ctf.linkextractor.entities.Page;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class DB {
    public static final DB singletone = new DB("db/");

    private ConcurrentHashMap<String, User> users = new ConcurrentHashMap<>();

    private ConcurrentHashMap<Integer, Page> pages = new ConcurrentHashMap<>();
    private AtomicInteger lastPageId;

    private ConcurrentHashMap<Integer, Link> links = new ConcurrentHashMap<>();
    private AtomicInteger lastLinkId;


    private OutputStream usersOutputFileStream;
    private ObjectOutputStream usersOutputObjectStream;

    private OutputStream pagesOutputFileStream;
    private ObjectOutputStream pagesOutputObjectStream;

    private OutputStream linksOutputFileStream;
    private ObjectOutputStream linksOutputObjectStream;



    //TODO make consistent usage of var/explicit types
    public DB(String dbDir) {
        Path dbPaths = Paths.get(dbDir);
        try {
            Files.createDirectories(dbPaths);

            var usersFilePath = Paths.get(dbDir, "users");
            if(Files.exists(usersFilePath))
            {
                LoadUsers(usersFilePath);
                usersOutputFileStream = new SkippingFirstNBytesOutputStream(new FileOutputStream(usersFilePath.toString(), true), 4);
            }
            else
                usersOutputFileStream = new FileOutputStream(usersFilePath.toString(), true);
            usersOutputObjectStream = new ObjectOutputStream(usersOutputFileStream);


            var pagesFilePath = Paths.get(dbDir, "pages");
            if(Files.exists(pagesFilePath))
            {
                LoadPages(pagesFilePath);
                pagesOutputFileStream = new SkippingFirstNBytesOutputStream(new FileOutputStream(pagesFilePath.toString(), true), 4);
            }
            else
                pagesOutputFileStream = new FileOutputStream(pagesFilePath.toString(), true);
            pagesOutputObjectStream = new ObjectOutputStream(pagesOutputFileStream);

            lastPageId = new AtomicInteger(pages.size() > 0 ? Collections.max(pages.values().stream().map(p -> p.getId()).toList()) : 0);


            var linksFilePath = Paths.get(dbDir, "links");
            if(Files.exists(linksFilePath))
            {
                LoadLinks(linksFilePath);
                linksOutputFileStream = new SkippingFirstNBytesOutputStream(new FileOutputStream(linksFilePath.toString(), true), 4);
            }
            else
                linksOutputFileStream = new FileOutputStream(linksFilePath.toString(), true);
            linksOutputObjectStream = new ObjectOutputStream(linksOutputFileStream);

            lastLinkId = new AtomicInteger(links.size() > 0 ? Collections.max(links.values().stream().map(p -> p.getId()).toList()) : 0);

        } catch (IOException e) {
            throw new RuntimeException("Failed to initialize from disk", e);
        }
    }

    private void LoadUsers(Path usersFilePath) throws IOException {
        try (var inputStream = new FileInputStream(usersFilePath.toString());
             var objectInputStream = new ObjectInputStream(inputStream)) {

            //TODO is that correct? what about buffering?
            while(inputStream.available() > 0)
            {
                try {
                    TryAddUserToMemory((User)objectInputStream.readObject());
                } catch (ClassNotFoundException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }

    private void LoadPages(Path pagesFilePath) throws IOException {
        try (var inputStream = new FileInputStream(pagesFilePath.toString());
             var objectInputStream = new ObjectInputStream(inputStream)) {

            while (inputStream.available() > 0) {
                try {
                    AddPageToMemory((Page) objectInputStream.readObject());
                } catch (ClassNotFoundException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }

    private void LoadLinks(Path linksFilePath) throws IOException {
        try (var inputStream = new FileInputStream(linksFilePath.toString());
             var objectInputStream = new ObjectInputStream(inputStream)) {

            while (inputStream.available() > 0) {
                try {
                    AddLinkToMemory((Link) objectInputStream.readObject());
                } catch (ClassNotFoundException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }


    public User registerNewUser(UserRegisterModel model){
        var user = new User(model.getLogin(), model.getPassword());
        if(TryAddUserToMemory(user)){
            try {
                PersistUser(user);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            return user;
        }
        return null;
    }

    private boolean TryAddUserToMemory(User user){
        return users.putIfAbsent(user.getLogin(), user) == null;
    }

    private synchronized void PersistUser(User user) throws IOException {
        usersOutputObjectStream.writeObject(user);
        usersOutputObjectStream.flush();
    }

    public User findUserByLogin(String login){
        return users.get(login);
    }




    public Page addPage(String user, String url){
        var id = lastPageId.incrementAndGet();
        var page = new Page(id, user, url);
        AddPageToMemory(page);
        try {
            PersistPage(page);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return page;
    }

    private void AddPageToMemory(Page page){
        pages.put(page.getId(), page);
    }

    private synchronized void PersistPage(Page page) throws IOException {
        pagesOutputObjectStream.writeObject(page);
        pagesOutputObjectStream.flush();
    }

    public List<Page> getUserPages(String user) {
        return pages.values().stream().filter(p -> p.getUser().equals(user)).toList();
    }

    public Page getPageById(int id){
        return pages.get(id);
    }




    public Link addLink(int linkId, String url){
        var id = lastLinkId.incrementAndGet();
        var link = new Link(id, linkId, url);

        AddLinkToMemory(link);
        try {
            PersistLink(link);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return link;
    }

    private void AddLinkToMemory(Link link){
        links.put(link.getId(), link);
    }

    private synchronized void PersistLink(Link link) throws IOException {
        linksOutputObjectStream.writeObject(link);
        linksOutputObjectStream.flush();
    }

    public List<Link> getLinksByPageId(int pageId){
        return links.values().stream().filter(l -> l.getPageId() == pageId).toList();
    }

    public Link getLinkById(int id){
        return links.get(id);
    }
}
