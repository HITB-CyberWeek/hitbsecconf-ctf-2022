using System;
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

    public async Task BuildIndexesAsync()
    {
        var ttlIndex = Builders<UserMongoDocument>.IndexKeys.Ascending(d => d.CreatedUtcDate);
        var ttlOptions = new CreateIndexOptions<UserMongoDocument> { ExpireAfter = TimeSpan.FromMinutes(20) };
        await _collection.Indexes.CreateOneAsync(new CreateIndexModel<UserMongoDocument>(ttlIndex, ttlOptions));
    }

    public async Task<string> GetPasswordHashAsync(string username)
    {
        var filter = Builders<UserMongoDocument>.Filter.Eq(d => d.Username, username);
        return (await _collection.FindAsync(filter)).FirstOrDefault()?.PasswordHash;
    }

    public async Task AddUser(string username, string passwordHash)
    {
        var doc = new UserMongoDocument
            { Username = username, PasswordHash = passwordHash, CreatedUtcDate = DateTime.UtcNow };
        await _collection.InsertOneAsync(doc);
    }
}