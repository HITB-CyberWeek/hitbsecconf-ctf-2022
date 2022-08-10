using System.Threading.Tasks;

namespace App.Repositories;

public interface IUserRepository
{
    Task<string> GetPasswordHashAsync(string username);

    Task AddUser(string username, string passwordHash);
}