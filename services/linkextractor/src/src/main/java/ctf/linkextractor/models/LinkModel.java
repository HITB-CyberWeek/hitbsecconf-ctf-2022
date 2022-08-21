package ctf.linkextractor.models;

public class LinkModel {
    String url;

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public LinkModel(String url) {
        this.url = url;
    }
}
