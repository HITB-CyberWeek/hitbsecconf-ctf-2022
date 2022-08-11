using System;
using System.Threading.Tasks;
using App.Models;

namespace App.Repositories;

public interface INoteRepository
{
    Task<Note> GetAsync(Guid id, string user);
    Task<bool> SaveAsync(Note note, string user);
}