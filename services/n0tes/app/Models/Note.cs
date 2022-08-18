using System;

namespace App.Models;

public class Note
{
    public Guid Id { get; set; }

    public string Title { get; set; }

    public string Content { get; set; }

    public DateTime UpdatedUtcDate { get; set; }
}