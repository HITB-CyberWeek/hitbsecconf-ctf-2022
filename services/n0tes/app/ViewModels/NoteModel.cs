using System;

namespace App.ViewModels;

public class NoteModel
{
    public Guid Id { get; set; }

    public string Title { get; set; }

    public string Content { get; set; }
}