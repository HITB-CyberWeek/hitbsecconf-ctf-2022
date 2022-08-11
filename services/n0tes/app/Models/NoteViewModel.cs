using System;
using System.ComponentModel.DataAnnotations;

namespace App.Models;

public class NoteViewModel
{
    [Required]
    public string Title { get; set; }

    public string Content { get; set; }

    public static NoteViewModel From(Note note)
    {
        return new NoteViewModel
        {
            Title = note.Title,
            Content = note.Content
        };
    }

    public Note ToNote(Guid noteId)
    {
        return new Note
        {
            Id = noteId,
            Title = Title,
            Content = Content
        };
    }
}