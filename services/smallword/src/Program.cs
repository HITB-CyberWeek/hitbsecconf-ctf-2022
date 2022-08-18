if(!File.Exists("settings/settings.ini"))
    File.WriteAllText("settings/settings.ini", $"key = {Guid.NewGuid()}");

var builder = WebApplication.CreateBuilder(args);

builder.Configuration
    .AddIniFile("settings/settings.ini");
builder.WebHost
    .UseKestrel(opts => opts.Limits.MaxRequestBodySize = 8192);
builder.Services
    .AddControllers(options => options.SuppressImplicitRequiredAttributeForNonNullableReferenceTypes = true)
    .AddJsonOptions(options => options.JsonSerializerOptions.IncludeFields = true);

var app = builder.Build();

app.UseFileServer();
app.UseRouting();
app.UseEndpoints(endpoints => endpoints.MapControllers());

app.Run();
