package ctf.linkextractor.controllers;

import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;
import ctf.linkextractor.services.UserService;
import io.javalin.http.BadRequestResponse;
import io.javalin.http.Context;
import io.javalin.http.HttpCode;
import io.javalin.http.UnauthorizedResponse;
import io.javalin.plugin.openapi.annotations.*;

public class UserController {

    @OpenApi(
            path = "/users",
            method = HttpMethod.POST,
            summary = "Register and/or login user",
            operationId = "registerOrLogin",
            tags = {"User"},
            requestBody = @OpenApiRequestBody(content = {@OpenApiContent(from = UserRegisterModel.class)}),
            responses = {
                    //TODO here and in other result models swagger descriptions
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

        User user = UserService.singletone.RegisterOrLoginUser(userCreationModel);

        if(user == null)
            throw new UnauthorizedResponse("invalid credentials");

        ctx.cookie("user", UserService.singletone.createUserCookie(user));
    }

    //TODO swagger now tries to parse result as json, but it's just a string
    @OpenApi(
            path = "/users/whoami",
            method = HttpMethod.GET,
            summary = "Whoami",
            operationId = "whoami",
            tags = {"User"},
            responses = {
            }
    )
    public static void whoami(Context ctx) {
        User user = ctx.attribute("user");
        ctx.result(user.getLogin());
    }
}
