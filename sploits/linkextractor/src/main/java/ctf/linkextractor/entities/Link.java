package ctf.linkextractor.entities;

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
        try {
            return new URL("http://example.com");
        } catch (MalformedURLException e) {
            throw new RuntimeException(e);
        }
    }

    private URL toAbsoluteUrl(String page_url, String link_url) throws MalformedURLException {
        throw new RuntimeException("");
    }
}
