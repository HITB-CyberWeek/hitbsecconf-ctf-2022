using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using App.Models;
using Microsoft.Extensions.Configuration;
using MongoDB.Driver;

namespace App.Repositories;

public class NoteRepository : INoteRepository
{
    private readonly IMongoCollection<NoteMongoDocument> _collection;
    private readonly TimeSpan _ttl;

    public NoteRepository(IMongoCollection<NoteMongoDocument> collection, IConfiguration configuration)
    {
        _collection = collection;
        _ttl = configuration.GetValue<TimeSpan>("TTL");
    }

    public async Task BuildIndexesAsync()
    {
        var userIndex = Builders<NoteMongoDocument>.IndexKeys.Ascending(d => d.User)
            .Descending(d => d.UpdatedUtcDate);
        var ttlIndex = Builders<NoteMongoDocument>.IndexKeys.Ascending(d => d.CreatedUtcDate);
        var ttlOptions = new CreateIndexOptions<NoteMongoDocument> { ExpireAfter = _ttl };
        await _collection.Indexes.CreateManyAsync(new[]
        {
            new CreateIndexModel<NoteMongoDocument>(userIndex),
            new CreateIndexModel<NoteMongoDocument>(ttlIndex, ttlOptions)
        });
    }

    public async Task<IEnumerable<Note>> GetAllAsync(string user)
    {
        var filter = Builders<NoteMongoDocument>.Filter.Eq(d => d.User, user);
        var sort = Builders<NoteMongoDocument>.Sort.Descending(d => d.UpdatedUtcDate);
        var options = new FindOptions<NoteMongoDocument> { Sort = sort };
        return (await _collection.FindAsync(filter, options)).ToEnumerable().Select(d => d.ToNote());
    }

    public async Task<IEnumerable<NoteMongoDocument>> GetAllAsync()
    {
        var filter = Builders<NoteMongoDocument>.Filter.Empty;
        return (await _collection.FindAsync(filter)).ToEnumerable();
    }

    public async Task<Note> GetAsync(Guid id, string user)
    {
        var filter = Builders<NoteMongoDocument>.Filter.And(
            Builders<NoteMongoDocument>.Filter.Eq(d => d.Id, id),
            Builders<NoteMongoDocument>.Filter.Eq(d => d.User, user));
        var doc = (await _collection.FindAsync(filter)).FirstOrDefault();
        return doc?.ToNote();
    }

    public async Task<bool> SaveAsync(Note note, string user)
    {
        var doc = NoteMongoDocument.From(note, user);

        var filter = Builders<NoteMongoDocument>.Filter.And(
            Builders<NoteMongoDocument>.Filter.Eq(d => d.Id, note.Id),
            Builders<NoteMongoDocument>.Filter.Eq(d => d.User, user));
        var update = Builders<NoteMongoDocument>.Update.Set(d => d.Title, note.Title)
            .Set(d => d.Content, note.Content)
            .SetOnInsert(d => d.CreatedUtcDate, DateTime.UtcNow)
            .Set(d => d.UpdatedUtcDate, DateTime.UtcNow);
        try
        {
            await _collection.UpdateOneAsync(filter, update, new UpdateOptions { IsUpsert = true });
            return true;
        }
        catch (MongoDuplicateKeyException)
        {
            return false;
        }
    }

    public async Task DeleteAsync(Guid noteId, string user)
    {
        var filter = Builders<NoteMongoDocument>.Filter.And(
            Builders<NoteMongoDocument>.Filter.Eq(d => d.Id, noteId),
            Builders<NoteMongoDocument>.Filter.Eq(d => d.User, user));
        await _collection.DeleteOneAsync(filter);
    }
}