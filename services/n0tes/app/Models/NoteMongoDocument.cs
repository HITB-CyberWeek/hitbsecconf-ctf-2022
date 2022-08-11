using System;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace App.Models;

public class NoteMongoDocument
{
    [BsonId]
    [BsonRepresentation(BsonType.String)]
    public Guid Id { get; set; }

    [BsonElement("user")]
    public string User { get; set; }

    [BsonElement("title")]
    public string Title { get; set; }

    [BsonElement("content")]
    public string Content { get; set; }

    public Note ToNote()
    {
        return new Note
        {
            Id = Id,
            Title = Title,
            Content = Content
        };
    }

    public static NoteMongoDocument From(Note note, string user)
    {
        return new NoteMongoDocument
        {
            Id = note.Id,
            User = user,
            Title = note.Title,
            Content = note.Content
        };
    }
}