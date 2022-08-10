using MongoDB.Bson.Serialization.Attributes;

namespace App.Models;

public class UserMongoDocument
{
    [BsonId]
    public string Username { get; set; }

    [BsonElement("password_hash")]
    public string PasswordHash { get; set; }
}