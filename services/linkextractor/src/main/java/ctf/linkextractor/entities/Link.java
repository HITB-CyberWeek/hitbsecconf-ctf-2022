package ctf.linkextractor.entities;

import ctf.linkextractor.DB;

import java.io.Serializable;
import java.net.MalformedURLException;
import java.net.URL;

public class Link implements Serializable {
    private int id;
    private int pageId;
    private String parsed_url;

    public int getId() {
        return id;
    }

    public int getPageId() {
        return pageId;
    }

    public String getParsed_url() {
        return parsed_url;
    }

    @Override
    public int hashCode() {
        URL url = toUrl();
        if(url == null)
            return 0;
        return url.hashCode();
    }

    @Override
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof Link)) {
            return false;
        }
        var rhs = (Link) o;

        if(rhs == null)
            return false;
        var o1url = this.toUrl();
        var o2url = rhs.toUrl();
        if(o1url == null && o2url == null)
            return true;
        if(o1url == null || o1url == null)
            return false;
        return o1url.equals(o2url);
    }

    public Link(int id, int pageId, String parsed_url) {
        this.id = id;
        this.pageId = pageId;
        this.parsed_url = parsed_url;
    }

    public URL toUrl(){
        var page = DB.singletone.getPageById(pageId);
        if(page == null)
            return null;
        try {
            return toAbsoluteUrl(page.getUrl(), parsed_url);
        } catch (MalformedURLException e) {
            return null;
        }
    }

    //TODO add caching
    private URL toAbsoluteUrl(String page_url, String link_url) throws MalformedURLException {
        if (link_url.contains("://"))
            return new URL(link_url);
        if (link_url.startsWith("//"))
            return new URL(new URL(page_url).getProtocol() + ":" + link_url);
        if (link_url.startsWith("/"))
        {
            var pageUrl = new URL(page_url);
            return new URL(pageUrl.getProtocol() + "://" + pageUrl.getAuthority() + link_url);
        }
        if (link_url.startsWith("../")){
            var pageProtocol = new URL(page_url).getProtocol();
            int pos = page_url.lastIndexOf("/");
            String baseUrl;
            if(pos == -1 || (baseUrl = page_url.substring(0, pos + 1)).equals(pageProtocol + "://")){
                return new URL(page_url + "/" + link_url);
            }
            //TODO case domain/../path can also be simplified
            return new URL(baseUrl + link_url);
        }
        return new URL(page_url + link_url);
    }
}
