package ctf.linkextractor.controllers;

import ctf.linkextractor.entities.Page;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.PageLinksModel;
import ctf.linkextractor.models.PageModel;
import ctf.linkextractor.services.PageService;
import io.javalin.http.Context;
import io.javalin.http.ForbiddenResponse;
import io.javalin.http.NotFoundResponse;
import io.javalin.plugin.openapi.annotations.*;

import java.net.URL;
import java.util.List;

public class PageController {
    @OpenApi(
            path = "/pages",
            method = HttpMethod.POST,
            summary = "Parse links from html",
            operationId = "parse",
            queryParams = {@OpenApiParam(name = "url", description = "url of the html page", required = true)},
            tags = {"Page"},
            requestBody = @OpenApiRequestBody(content = {@OpenApiContent(from = String.class)}, description = "html page with urls to parse"),
            responses = {
                @OpenApiResponse(status = "200", content = {@OpenApiContent(from = PageModel.class)})
            }
    )
    public static void parse(Context ctx) {
        String pageUrl = validQueryParamUrl(ctx);
        User user = ctx.attribute("user");
        PageModel pageModel = PageService.singletone.parseAndAddPage(user.getLogin(), pageUrl, ctx.body());

        ctx.json(pageModel);
    }

    @OpenApi(
            path = "/pages",
            method = HttpMethod.GET,
            summary = "Get user pages",
            operationId = "getAll",
            tags = {"Page"},
            responses = {
                @OpenApiResponse(status = "200", content = {@OpenApiContent(from = PageModel[].class)})
            }
    )
    public static void getAll(Context ctx) {
        User user = ctx.attribute("user");
        ctx.json(PageService.singletone.getPages(user));
    }

    @OpenApi(
            path = "/pages/{pageId}",
            method = HttpMethod.GET,
            summary = "Get page links",
            operationId = "getOne",
            pathParams = {@OpenApiParam(name = "pageId", type = Integer.class, description = "pageId")},
            tags = {"Page"},
            responses = {
                @OpenApiResponse(status = "404"),
                @OpenApiResponse(status = "200", content = {@OpenApiContent(from = PageLinksModel.class)})
            }
    )
    public static void getOne(Context ctx) {
        Integer pageId = validPathParamPageId(ctx);
        User user = ctx.attribute("user");
        Page page = PageService.singletone.getPage(pageId);
        if(page == null)
            throw new NotFoundResponse("Requested page not found");
        if(!user.getLogin().equals(page.getUser()))
            throw new ForbiddenResponse("Forbidden");

        ctx.json(PageService.singletone.getDistinctLinks(pageId));
    }

    private static String validQueryParamUrl(Context ctx) {
        return ctx.queryParamAsClass("url", String.class).check(s -> {
            try {
                new URL(s);
                return true;
            }
            catch (Exception e) {
                return false;
            }
        }, "url is invalid").get();
    }

    private static int validPathParamPageId(Context ctx) {
        return ctx.pathParamAsClass("pageId", Integer.class).check(id -> id > 0, "ID must be greater than 0").get();
    }
}
