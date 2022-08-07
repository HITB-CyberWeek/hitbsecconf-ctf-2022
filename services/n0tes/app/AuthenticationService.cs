namespace App;

public class AuthenticationService : IAuthenticationService
{
    public AuthenticationState LoginOrRegister(string username, string password)
    {
        if (username == "user")
        {
            if (password == "user")
                return AuthenticationState.Success;
            return AuthenticationState.WrongPassword;
        }

        return AuthenticationState.UserCreated;
    }
}