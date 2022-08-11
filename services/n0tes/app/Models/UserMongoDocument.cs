using System;
using MongoDB.Bson.Serialization.Attributes;

namespace App.Models;

public class UserMongoDocument
{
    [BsonId]
    public string Username { get; set; }

    [BsonElement("password_hash")]
    public string PasswordHash { get; set; }

    [BsonElement("created")]
    [BsonDateTimeOptions(Kind = DateTimeKind.Utc)]
    public DateTime CreatedUtcDate { get; set; }
}