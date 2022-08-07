namespace App;

public interface IAuthenticationService
{
    AuthenticationState LoginOrRegister(string username, string password);
}