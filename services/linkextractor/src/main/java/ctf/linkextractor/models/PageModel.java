package ctf.linkextractor.models;

public class PageModel {
    int pageId;
    String pageUrl;
    int linksCount;

    public int getPageId() {
        return pageId;
    }

    public void setPageId(int pageId) {
        this.pageId = pageId;
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

    public PageModel(int pageId, String pageUrl, int linksCount) {
        this.pageId = pageId;
        this.pageUrl = pageUrl;
        this.linksCount = linksCount;
    }
}
