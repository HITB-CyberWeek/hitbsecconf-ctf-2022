using System.Threading.Tasks;

namespace App;

public interface IAuthenticationService
{
    Task<AuthenticationState> LoginOrRegisterAsync(string username, string password);
}