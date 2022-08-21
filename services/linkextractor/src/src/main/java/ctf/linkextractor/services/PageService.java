package ctf.linkextractor.services;

import ctf.linkextractor.DB;
import ctf.linkextractor.entities.Page;
import ctf.linkextractor.models.LinkModel;
import ctf.linkextractor.models.PageModel;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PageService {
    public static PageService singletone = new PageService();

    public void addPage(String user, String pageUrl, String body) {
        Pattern p = Pattern.compile(" href\s*=\s*\"(.+?)\"");
        Matcher m = p.matcher(body);
        String url;

        Page page = DB.addPage(user, pageUrl);

        while (m.find()) {
            url = m.group(1);
            DB.addLink(page.getId(), url);
        }
    }

    public Page getPage(int id) {
        return DB.getPageById(id);
    }

    //TODO don't expose PageModel and LinkModel, it's for controllers
    public List<PageModel> getPages(String user) {
        return DB.getUserPages(user).stream().map(p -> new PageModel(p.getId(), p.getUrl(), DB.getLinksByPageId(p.getId()).size())).toList();
    }

    public List<LinkModel> getUniqLinks(Integer pageId) {
        return DB.getLinksByPageId(pageId).stream().distinct().map(l -> new LinkModel(l.toUrl().toString())).toList();
    }
}
