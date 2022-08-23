package ctf.linkextractor.models;

import java.util.List;

public class PageLinksModel {
    int pageId;
    String pageUrl;
    List<LinkModel> links;

    public String getPageUrl() {
        return pageUrl;
    }

    public int getPageId() {
        return pageId;
    }

    public List<LinkModel> getLinks() {
        return links;
    }

    public PageLinksModel(int pageId, String pageUrl, List<LinkModel> links) {
        this.pageId = pageId;
        this.pageUrl = pageUrl;
        this.links = links;
    }

    public static final class LinkModel{
        int id;
        String url;

        public LinkModel(int id, String url) {
            this.id = id;
            this.url = url;
        }

        public int getId() {
            return id;
        }

        public String getUrl() {
            return url;
        }
    }
}
