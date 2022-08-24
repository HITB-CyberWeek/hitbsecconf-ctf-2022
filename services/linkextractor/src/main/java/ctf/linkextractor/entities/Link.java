package ctf.linkextractor.entities;

import ctf.linkextractor.DB;

import java.io.Serializable;
import java.net.MalformedURLException;
import java.net.URL;

public class Link implements Serializable {
    private int id;
    private int pageId;
    private String parsedUrl;

    public int getId() {
        return id;
    }

    public int getPageId() {
        return pageId;
    }

    public String getParsedUrl() {
        return parsedUrl;
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
        Link rhs = (Link) o;

        if(rhs == null)
            return false;
        URL o1url = this.toUrl();
        URL o2url = rhs.toUrl();
        if(o1url == null && o2url == null)
            return true;
        if(o1url == null || o1url == null)
            return false;
        return o1url.equals(o2url);
    }

    public Link(int id, int pageId, String parsedUrl) {
        this.id = id;
        this.pageId = pageId;
        this.parsedUrl = parsedUrl;
    }

    private URL resolvedUrl;
    public URL toUrl(){
        if(resolvedUrl == null)
            resolvedUrl = resolveUrl();
        return resolvedUrl;
    }

    private URL resolveUrl() {
        Page page = DB.singletone.getPageById(pageId);
        if(page == null)
            return null;
        try {
            return toAbsoluteUrl(page.getUrl(), parsedUrl);
        } catch (MalformedURLException e) {
            return null;
        }
    }

    private URL toAbsoluteUrl(String page_url, String link_url) throws MalformedURLException {
        if (link_url.contains("://"))
            return new URL(link_url);
        if (link_url.startsWith("//"))
            return new URL(new URL(page_url).getProtocol() + ":" + link_url);
        if (link_url.startsWith("/"))
        {
            URL pageUrl = new URL(page_url);
            return new URL(pageUrl.getProtocol() + "://" + pageUrl.getAuthority() + link_url);
        }
        if (link_url.startsWith("../")){
            String pageProtocol = new URL(page_url).getProtocol();
            int pos = page_url.lastIndexOf("/");
            String baseUrl;
            if(pos == -1 || (baseUrl = page_url.substring(0, pos + 1)).equals(pageProtocol + "://")){
                return new URL(page_url + "/" + link_url);
            }
            return new URL(baseUrl + link_url);
        }
        return new URL(page_url + link_url);
    }
}
