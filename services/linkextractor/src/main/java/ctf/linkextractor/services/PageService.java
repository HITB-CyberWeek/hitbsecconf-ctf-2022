package ctf.linkextractor.services;

import ctf.linkextractor.DB;
import ctf.linkextractor.entities.Page;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.PageLinksModel;
import ctf.linkextractor.models.PageModel;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PageService {
    public static PageService singletone = new PageService();

    public PageModel parseAndAddPage(String user, String pageUrl, String body) {
        Pattern p = Pattern.compile(" href\s*=\s*\"(.+?)\"");
        Matcher m = p.matcher(body);
        String url;

        Page page = DB.singletone.addPage(user, pageUrl);

        while (m.find()) {
            url = m.group(1);
            DB.singletone.addLink(page.getId(), url);
        }

        return new PageModel(page.getId(), page.getUrl(), getDistinctLinks(page.getId()).getLinks().size());
    }

    public Page getPage(int id) {
        return DB.singletone.getPageById(id);
    }

    public List<PageModel> getPages(User user) {
        if(user.pages == null)
            user.setPages(DB.singletone.getUserPages(user.getLogin()));

        return user.pages
                .stream()
                .map(p -> new PageModel(p.getId(), p.getUrl(), getDistinctLinks(p.getId()).getLinks().size()))
                .toList();
    }

    public PageLinksModel getDistinctLinks(Integer pageId) {
        Page page = DB.singletone.getPageById(pageId);

        if(page.links == null)
            page.setLinks(DB.singletone.getLinksByPageId(page.getId()));

        return new PageLinksModel(
                page.getId(),
                page.getUrl(),
                page.links
                        .stream()
                        .map(l -> new PageLinksModel.LinkModel(l.getId(), l.toUrl().toString()))
                        .toList());
    }
}
