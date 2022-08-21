package ctf.linkextractor;

import ctf.linkextractor.controllers.PageController;
import ctf.linkextractor.controllers.UserController;
import ctf.linkextractor.entities.Link;
import ctf.linkextractor.entities.User;
import ctf.linkextractor.services.UserService;
import io.javalin.Javalin;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashSet;

import io.javalin.core.security.RouteRole;
import io.javalin.plugin.openapi.OpenApiOptions;
import io.javalin.plugin.openapi.OpenApiPlugin;
import io.javalin.plugin.openapi.ui.SwaggerOptions;
import io.swagger.v3.oas.models.info.Info;
import org.apache.commons.codec.binary.Base64;

import static io.javalin.apibuilder.ApiBuilder.*;

public class Program {

    public static void main(String[] args) throws IOException {
        Javalin app = Javalin.create(config -> {
            config.registerPlugin(getConfiguredOpenApiPlugin());
            config.defaultContentType = "application/json";
            config.accessManager((handler, ctx, routeRoles) -> {
                Role userRole = Role.ANYONE;
                User user = UserService.singletone.parseUserCookie(ctx.cookie("user"));
                if(user != null)
                {
                    if(UserService.singletone.ValidateUser(user))
                    {
                        ctx.attribute("user", user.getLogin());
                        userRole = Role.USER;
                    }
                }

                if (routeRoles.contains(userRole)) {
                    handler.handle(ctx);
                } else {
                    {
                        ctx.status(401).result("Unauthorized");
                    }
                }
            });
        }).routes(() -> {
            path("pages", () -> {
                get(PageController::getAll, Role.USER);
                post(PageController::parse, Role.USER);
                path("{pageId}", () -> {
                    get(PageController::getOne, Role.USER);
                });
            });
            path("users", () -> {
                post(UserController::registerOrLogin, Role.USER, Role.ANYONE);
                path("whoami", () -> {
                    get(UserController::whoami, Role.USER);
                });
            });
        }).start("0.0.0.0",8080);
        System.out.println("Check out Swagger UI docs at http://localhost:8080/swagger-ui");
   }

    private static OpenApiPlugin getConfiguredOpenApiPlugin() {
        Info info = new Info().version("1.0").description("User API");
        OpenApiOptions options = new OpenApiOptions(info)
                .path("/swagger-docs")
                .activateAnnotationScanningFor("ctf.linkextractor")
                .swagger(new SwaggerOptions("/"))
                .roles(Role.ANYONE, Role.USER)
                .defaultDocumentation(doc -> {
//                    doc.json("500", InternalServerErrorResponse.class);//TODO more specific class
//                    doc.json("503", ServiceUnavailableResponse.class);
                });
        return new OpenApiPlugin(options);
    }

    enum Role implements RouteRole {
        ANYONE, USER;
    }
}

