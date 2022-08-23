package ctf.linkextractor.services;

import ctf.linkextractor.DB;
import ctf.linkextractor.entities.Page;
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

    public List<PageModel> getPages(String user) {
        return DB.singletone.getUserPages(user)
                .stream()
                .map(p -> new PageModel(p.getId(), p.getUrl(), getDistinctLinks(p.getId()).getLinks().size()))
                .toList();
    }

    public PageLinksModel getDistinctLinks(Integer pageId) {
        Page page = DB.singletone.getPageById(pageId);

        return new PageLinksModel(
                page.getId(),
                page.getUrl(),
                DB.singletone.getLinksByPageId(page.getId())
                        .stream()
                        .distinct()
                        .map(l -> new PageLinksModel.LinkModel(l.getId(), l.toUrl().toString()))
                        .toList());
    }
}
