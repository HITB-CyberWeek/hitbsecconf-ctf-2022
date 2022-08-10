using System.Threading.Tasks;
using App.Models;
using MongoDB.Driver;

namespace App.Repositories;

public class UserRepository : IUserRepository
{
    private readonly IMongoCollection<UserMongoDocument> _repository;

    public UserRepository(IMongoCollection<UserMongoDocument> repository)
    {
        _repository = repository;
    }

    public async Task<string> GetPasswordHashAsync(string username)
    {
        var filter = Builders<UserMongoDocument>.Filter.Eq(d => d.Username, username);
        return (await _repository.FindAsync(filter)).FirstOrDefault()?.PasswordHash;
    }

    public async Task AddUser(string username, string passwordHash)
    {
        var doc = new UserMongoDocument { Username = username, PasswordHash = passwordHash };
        await _repository.InsertOneAsync(doc);
    }
}