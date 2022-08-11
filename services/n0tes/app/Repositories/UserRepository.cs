using System.Threading.Tasks;
using App.Models;
using MongoDB.Driver;

namespace App.Repositories;

public class UserRepository : IUserRepository
{
    private readonly IMongoCollection<UserMongoDocument> _collection;

    public UserRepository(IMongoCollection<UserMongoDocument> collection)
    {
        _collection = collection;
    }

    public async Task<string> GetPasswordHashAsync(string username)
    {
        var filter = Builders<UserMongoDocument>.Filter.Eq(d => d.Username, username);
        return (await _collection.FindAsync(filter)).FirstOrDefault()?.PasswordHash;
    }

    public async Task AddUser(string username, string passwordHash)
    {
        var doc = new UserMongoDocument { Username = username, PasswordHash = passwordHash };
        await _collection.InsertOneAsync(doc);
    }
}