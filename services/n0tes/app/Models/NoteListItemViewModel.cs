using System;

namespace App.Models;

public class NoteListItemViewModel
{
    public Guid NoteId { get; set; }

    public string Title { get; set; }

    public DateTime UpdatedUtcDate { get; set; }

    public static NoteListItemViewModel From(Note note)
    {
        return new NoteListItemViewModel
        {
            NoteId = note.Id,
            Title = note.Title,
            UpdatedUtcDate = note.UpdatedUtcDate
        };
    }
}