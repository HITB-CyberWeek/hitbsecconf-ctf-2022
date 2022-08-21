package ctf.linkextractor.entities;

public class Page {
    private int id;
    private String user;
    private String url;

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
