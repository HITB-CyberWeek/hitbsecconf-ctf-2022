using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Serialization;
using CommunityToolkit.HighPerformance;
using CommunityToolkit.HighPerformance.Buffers;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;
using ProtoBuf;

[ProtoContract]
public class User
{
    [ProtoMember(1)] public DateTime? BirthDate;
    [ProtoMember(2)] public string? Gender;
    [ProtoMember(3)] public string? Country;
    [ProtoMember(4)] public string? Company;
    [ProtoMember(5)] public string? Address;
    [ProtoMember(6)] public string? Name;
    [ProtoMember(7)] public string? Surname;
    [ProtoMember(8)] public string? Patronymic;
    [ProtoMember(9)] public string? Login;
    [ProtoIgnore] public string? Password;
    [JsonIgnore] [ProtoMember(10)] public byte[]? Salt;
    [JsonIgnore] [ProtoMember(11)] public byte[]? PasswordHash;
    [ProtoMember(12)] public string? Hobby;
    [ProtoMember(13)] public DateTime Created;

    public Guid UserId => Login?.ToUserId() ?? Guid.Empty;
}

public static class UserProfile
{
    static UserProfile() => Directory.CreateDirectory(DataDirectoryPath);

    public static async Task<User?> Find(Guid userId, CancellationToken cancellationToken)
    {
        try
        {
            var path = GetProfilePath(userId);
            await using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read | FileShare.Delete);
            using var buffer = MemoryOwner<byte>.Allocate(Math.Min((int)stream.Length, MaxProfileSize)); //NOTE: async ops isn't currently supported by protobuf-net
            await stream.CopyToAsync(buffer.Memory.AsStream(), cancellationToken);
            return Serializer.Deserialize<User>(buffer.Span);
        }
        catch(FileNotFoundException) { return null; }
    }

    public static async Task<bool> TrySave(User user, CancellationToken cancellationToken)
    {
        try
        {
            var path = GetProfilePath(user.UserId);
            using var buffer = MemoryOwner<byte>.Allocate(MaxProfileSize); //NOTE: async ops isn't currently supported by protobuf-net
            var writer = new MemoryBufferWriter<byte>(buffer.Memory);
            Serializer.Serialize(writer, user);
            await using var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None);
            await writer.WrittenMemory.AsStream().CopyToAsync(stream, cancellationToken);
            return true;
        }
        catch(IOException) { return false; }
    }

    public static FileStream? TryReadFile(Guid userId, Guid fileId)
        => TryOpenFile(userId, fileId, FileMode.Open, FileAccess.Read, FileShare.Read | FileShare.Delete);

    public static FileStream? TryUpdateFile(Guid userId, Guid fileId)
        => TryOpenFile(userId, fileId, FileMode.Create, FileAccess.Write, FileShare.Read | FileShare.Delete);

    private static FileStream? TryOpenFile(Guid userId, Guid fileId, FileMode mode, FileAccess access, FileShare share)
    {
        try { return new FileStream(Path.Combine(GetDocsDirectoryPath(userId), fileId + ".html"), mode, access, share, 4096, FileOptions.Asynchronous); }
        catch(FileNotFoundException) when((access & FileAccess.Read) != 0) { return null; }
        catch(IOException e) when((access & FileAccess.Write) != 0 && (e.HResult == 0x20 || e.HResult == 0x21)) { return null; }
    }

    public static IEnumerable<string?> ListFiles(Guid userId)
        => Directory.EnumerateFiles(GetDocsDirectoryPath(userId), "*.html", SearchOption.TopDirectoryOnly)
            .OrderByDescending(File.GetLastWriteTimeUtc)
            .Take(10)
            .Select(Path.GetFileNameWithoutExtension);

    private static string GetUserDirectoryPath(Guid userId)
    {
        var str = userId.ToString();
        var path = Path.Combine(DataDirectoryPath, str[..2], str[2..4], str);
        Directory.CreateDirectory(path);
        return path;
    }

    private static string GetProfilePath(Guid userId)
        => Path.Combine(GetUserDirectoryPath(userId), "profile");

    private static string GetDocsDirectoryPath(Guid userId)
    {
        var path = Path.Combine(GetUserDirectoryPath(userId), DocsDirectoryPath);
        Directory.CreateDirectory(path);
        return path;
    }

    private const string DataDirectoryPath = "data/";
    private const string DocsDirectoryPath = "docs/";

    private const int MaxProfileSize = 8192;
}

public static class AuthHelper
{
    public static Guid? Auth(this HttpRequest request, byte[] key)
    {
        var auth = request.Cookies["auth"];
        if(auth == null)
            return null;
        var parts = auth.Split(Delim);
        if(parts.Length != 2 || parts[0] == string.Empty)
            return null;
        var (login, hmac) = (parts[0], parts[1]);
        using var buffer = SpanOwner<byte>.Allocate(hmac.Length / 4 * 3);
        if(!Convert.TryFromBase64String(hmac, buffer.Span, out var count) || count == 0)
            return null;
        if(!CryptographicOperations.FixedTimeEquals(Hmac(login, key), buffer.Span.Slice(0, count)))
            return null;
        return login.ToUserId();
    }

    public static void SetAuth(this HttpResponse response, string login, byte[] key)
        => response.Cookies.Append("auth", $"{login}{Delim}{Convert.ToBase64String(Hmac(login, key))}");

    public static Guid ToUserId(this string login)
        => new(SHA256.HashData(Encoding.UTF8.GetBytes(login))[..16]);

    private static byte[] Hmac(string login, byte[] key)
        => HMACSHA256.HashData(key, login.ToUserId().ToByteArray());

    private const char Delim = ' ';
}

public static class PasswordHelper
{
    public static bool IsPasswordCorrect(string password, byte[] salt, byte[] hash, byte[] pepper)
        => CryptographicOperations.FixedTimeEquals(HashPassword(password, salt, pepper), hash);

    public static (byte[] Salt, byte[] Hash) HashPassword(string password, byte[] pepper)
    {
        var salt = RandomNumberGenerator.GetBytes(12);
        return (salt, HashPassword(password, salt, pepper));
    }

    private static byte[] HashPassword(string password, byte[] salt, byte[] pepper)
        => KeyDerivation.Pbkdf2(password, salt, KeyDerivationPrf.HMACSHA256, iterationCount: 7, 256 / 8).Select((b, i) => (byte)(b ^ pepper[i % pepper.Length])).ToArray();
}
