package ctf.linkextractor.entities;

import java.io.ObjectInputFilter;
import java.io.Serializable;
import java.util.HashSet;
import java.util.List;

public class Page implements Serializable {
    private int id;
    private String user;
    private String url;

    public HashSet<Link> links;
    public void setLinks(List<Link> l){
        links = new HashSet<>(l);
    }

    public int getId() {
        return id;
    }

    public String getUser() {
        return user;
    }

    public String getUrl() {
        return url;
    }

    public Page(int id, String user, String url) {
        this.id = id;
        this.user = user;
        this.url = url;
    }
}
