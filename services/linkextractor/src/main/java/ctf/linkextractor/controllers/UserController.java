package ctf.linkextractor.controllers;

import ctf.linkextractor.entities.User;
import ctf.linkextractor.models.UserRegisterModel;
import ctf.linkextractor.services.UserService;
import io.javalin.http.Context;
import io.javalin.http.HttpCode;
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
            }
    )
    public static void registerOrLogin(Context ctx) throws Exception {
        UserRegisterModel userCreationModel;
        try {
            userCreationModel = ctx.bodyAsClass(UserRegisterModel.class);
        }
        catch (Exception e){
            ctx.status(HttpCode.BAD_REQUEST).result("Can't parse request model");
            return;
        }

        User user = UserService.singletone.RegisterOrLoginUser(userCreationModel);

        if(user == null)
            throw new Exception("invalid credentials");

        //TODO move to common place with usage in accessManager
        ctx.cookie("user", UserService.singletone.createUserCookie(user));
    }

    //TODO swagger now tries to parse reulst as json, but it's just a string
    @OpenApi(
            path = "/users/whoami",
            method = HttpMethod.GET,
            summary = "Whoami",
            operationId = "whoami",
            tags = {"User"},
            responses = {
            }
    )
    public static void whoami(Context ctx) throws Exception {
        String user = ctx.attribute("user");
        ctx.result(user);
    }
}