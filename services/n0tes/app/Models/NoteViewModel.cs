using System;

namespace App.Models;

public class NoteViewModel
{
    public Guid Id { get; set; }

    public string Title { get; set; }

    public string Content { get; set; }
}