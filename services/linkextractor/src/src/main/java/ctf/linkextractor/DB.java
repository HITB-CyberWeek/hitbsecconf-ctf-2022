package ctf.linkextractor;

import ctf.linkextractor.entities.Link;
import ctf.linkextractor.entities.Page;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class DB {
    static ConcurrentHashMap<String, User> users = new ConcurrentHashMap<>();

    static ConcurrentHashMap<Integer, Page> pages = new ConcurrentHashMap<>();
    static AtomicInteger lastPageId = new AtomicInteger(0);

    static ConcurrentHashMap<Integer, Link> links = new ConcurrentHashMap<>();
    static AtomicInteger lastLinkId = new AtomicInteger(0);


    public static User findUserByLogin(String login){
        return users.get(login);
    }

    public static User registerUser(UserRegisterModel model){
        var user = new User(model.getLogin(), model.getPassword());
        boolean success = users.putIfAbsent(model.getLogin(), user) == null;
        return success ? user : null;
    }

    public static List<Page> getUserPages(String user) {
        return pages.values().stream().filter(p -> {
            return p.getUser().equals(user);
        }).toList();
    }


    public static Page getPageById(int id){
        return pages.get(id);
    }

    public static Page addPage(String user, String url){
        var id = lastPageId.incrementAndGet();
        var page = new Page(id, user, url);
        pages.put(id, page);
        return page;
    }

    public static List<Link> getLinksByPageId(int id){
        return links.values().stream().filter(l -> l.getId() == id).toList();
    }


    public static Link getLinkById(int id){
        return links.get(id);
    }


    public static Link addLink(int pageId, String url){
        var id = lastLinkId.incrementAndGet();
        var link = new Link(id, pageId, url);
        links.put(id, link);
        return link;
    }


}
