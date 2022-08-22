using System;
using System.Text.Json.Serialization;
using checker.smallword;

namespace checker
{
	internal class PutResult
	{
		[JsonPropertyName("public_flag_id")] public string PublicFlagId { get; set; }

		[JsonPropertyName("user")] public User User { get; set; }
		[JsonPropertyName("fileId")] public Guid FileId { get; set; }
		[JsonPropertyName("image")] public string Base64Image { get; set; }
		[JsonPropertyName("cookie")] public string Cookie { get; set; }
	}
}
