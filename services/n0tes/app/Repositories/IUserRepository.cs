using System.Threading.Tasks;

namespace App.Repositories;

public interface IUserRepository
{
    Task BuildIndexesAsync();
    Task<string> GetPasswordHashAsync(string username);
    Task AddUser(string username, string passwordHash);
}