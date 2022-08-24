package ctf.linkextractor.controllers;

import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;
import ctf.linkextractor.services.UserService;
import io.javalin.http.BadRequestResponse;
import io.javalin.http.Context;
import io.javalin.http.UnauthorizedResponse;
import io.javalin.plugin.openapi.annotations.*;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class UserController {

    static Pattern loginRegex = Pattern.compile("^[a-zA-Z0-9$@()'._\\-]{1,32}$");

    @OpenApi(
            path = "/users",
            method = HttpMethod.POST,
            summary = "Register and/or login user",
            operationId = "registerOrLogin",
            tags = {"User"},
            requestBody = @OpenApiRequestBody(content = {@OpenApiContent(from = UserRegisterModel.class)}),
            responses = {
                @OpenApiResponse(status = "200"),
            }
    )
    public static void registerOrLogin(Context ctx) throws Exception {
        UserRegisterModel userCreationModel;
        try {
            userCreationModel = ctx.bodyAsClass(UserRegisterModel.class);
        }
        catch (Exception e){
            throw new BadRequestResponse("Can't parse request model");
        }

        Matcher m = loginRegex.matcher(userCreationModel.getLogin());
        if(!m.matches())
            throw new BadRequestResponse("login is too long or has invalid characters");

        User user = UserService.singletone.RegisterOrLoginUser(userCreationModel);

        if(user == null)
            throw new UnauthorizedResponse("invalid credentials");

        ctx.cookie("user", UserService.singletone.createUserCookie(user));
    }

    @OpenApi(
            path = "/users/whoami",
            method = HttpMethod.GET,
            summary = "Whoami",
            operationId = "whoami",
            tags = {"User"},
            responses = {
                @OpenApiResponse(status = "200", content = {@OpenApiContent(from = String.class)})
            }
    )
    public static void whoami(Context ctx) {
        User user = ctx.attribute("user");
        ctx.result(user.getLogin());
    }
}
