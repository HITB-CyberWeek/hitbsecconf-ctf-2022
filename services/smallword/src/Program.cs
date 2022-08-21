using System.Net;
using System.Security.Cryptography;

const string settingsFilePath = "settings/settings.ini";

if(!File.Exists(settingsFilePath))
{
    Directory.CreateDirectory(Path.GetDirectoryName(settingsFilePath)!);
    File.WriteAllText(settingsFilePath, $"key = {new Guid(RandomNumberGenerator.GetBytes(16))}");
}

var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddIniFile(settingsFilePath);
builder.WebHost
    .UseKestrel(opts =>
    {
        opts.Listen(IPAddress.Any, 5000);
        opts.Limits.MaxRequestBodySize = 8192;
    });
builder.Services
    .AddControllers(options => options.SuppressImplicitRequiredAttributeForNonNullableReferenceTypes = true)
    .AddJsonOptions(options => options.JsonSerializerOptions.IncludeFields = true);

var app = builder.Build();

app.UseFileServer();
app.UseRouting();
app.UseEndpoints(endpoints => endpoints.MapControllers());

app.Run();
