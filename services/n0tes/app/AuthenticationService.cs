using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using App.Repositories;

namespace App;

public class AuthenticationService : IAuthenticationService
{
    private readonly IUserRepository _userRepository;

    public AuthenticationService(IUserRepository userRepository)
    {
        _userRepository = userRepository;
    }

    public async Task<AuthenticationState> LoginOrRegisterAsync(string username, string password)
    {
        var oldHash = await _userRepository.GetPasswordHashAsync(username);
        var newHash = GetHash(password);

        if (oldHash != null)
        {
            return oldHash == newHash ? AuthenticationState.Success : AuthenticationState.WrongPassword;
        }

        await _userRepository.AddUser(username, newHash);
        return AuthenticationState.UserCreated;
    }

    private static string GetHash(string password)
    {
        using (var hashAlgo = SHA256.Create())
        {
            var data = hashAlgo.ComputeHash(Encoding.UTF8.GetBytes(password));

            var builder = new StringBuilder();
            for (int i = 0; i < data.Length; i++)
            {
                builder.Append(data[i].ToString("x2"));
            }

            return builder.ToString();
        }
    }
}