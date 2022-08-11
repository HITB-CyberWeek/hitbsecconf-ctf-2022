using System;
using System.Threading.Tasks;
using App.Models;
using MongoDB.Driver;

namespace App.Repositories;

public class NoteRepository : INoteRepository
{
    private readonly IMongoCollection<NoteMongoDocument> _collection;

    public NoteRepository(IMongoCollection<NoteMongoDocument> collection)
    {
        _collection = collection;
    }

    public async Task BuildIndexesAsync()
    {
        var indexKeys = Builders<NoteMongoDocument>.IndexKeys.Ascending(d => d.User);
        await _collection.Indexes.CreateOneAsync(new CreateIndexModel<NoteMongoDocument>(indexKeys));
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
            .Set(d => d.Content, note.Content);
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
}