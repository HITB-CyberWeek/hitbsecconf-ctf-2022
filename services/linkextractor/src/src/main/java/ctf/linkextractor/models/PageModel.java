package ctf.linkextractor.models;

public class PageModel {
    int id;
    String pageUrl;
    int linksCount;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getPageUrl() {
        return pageUrl;
    }

    public void setPageUrl(String pageUrl) {
        this.pageUrl = pageUrl;
    }

    public int getLinksCount() {
        return linksCount;
    }

    public void setLinksCount(int linksCount) {
        this.linksCount = linksCount;
    }

    public PageModel(int id, String pageUrl, int linksCount) {
        this.id = id;
        this.pageUrl = pageUrl;
        this.linksCount = linksCount;
    }
}
