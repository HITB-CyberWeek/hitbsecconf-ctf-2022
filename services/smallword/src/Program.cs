using System.Net;
using System.Security.Cryptography;

const string settingsFilePath = "settings/settings.ini";

if(!File.Exists(settingsFilePath))
{
    Directory.CreateDirectory(Path.GetDirectoryName(settingsFilePath)!);
    File.WriteAllText(settingsFilePath, $"key = {Convert.ToBase64String(RandomNumberGenerator.GetBytes(24))}");
}

var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddIniFile(settingsFilePath);
builder.Logging
    .ClearProviders();
builder.WebHost
    .UseKestrel(opts =>
    {
        opts.Listen(IPAddress.Any, 5000);
        opts.Limits.MaxRequestBodySize = 8192;
        opts.Limits.MaxRequestHeadersTotalSize = 4096;
    });
builder.Services
    .AddControllers(options => options.SuppressImplicitRequiredAttributeForNonNullableReferenceTypes = true)
    .AddJsonOptions(options => options.JsonSerializerOptions.IncludeFields = true);

var app = builder.Build();

app.UseFileServer();
app.UseRouting();
app.UseEndpoints(endpoints => endpoints.MapControllers());

app.Run();
