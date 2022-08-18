using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using App.Models;

namespace App.Repositories;

public interface INoteRepository
{
    Task BuildIndexesAsync();
    Task<IEnumerable<Note>> GetAllAsync(string user);
    Task<IEnumerable<NoteMongoDocument>> GetAllAsync();
    Task<Note> GetAsync(Guid id, string user);
    Task<bool> SaveAsync(Note note, string user);
    Task DeleteAsync(Guid noteId, string user);
}