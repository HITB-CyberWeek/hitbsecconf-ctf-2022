using System.Text;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Net.Http.Headers;

[ApiController]
public class Handlers : Controller
{
    public Handlers(IConfiguration config)
        => this.config = config;

    [HttpPost("/register")]
    public async Task<IActionResult> Register([FromBody] User? user)
    {
        if(user == null || string.IsNullOrEmpty(user.Login = user.Login?.Trim()) || !user.Login.All(c => c == '_' || char.IsAscii(c) && char.IsLetterOrDigit(c)) || string.IsNullOrEmpty(user.Password))
            return StatusCode(400);

        (user.Salt, user.PasswordHash) = PasswordHelper.HashPassword(user.Password, Key);
        user.Created = DateTime.UtcNow;

        if(!await UserProfile.TrySave(user, HttpContext.RequestAborted))
            return StatusCode(409);

        Response.SetAuth(user.Login, Key);
        return Ok(user);
    }

    [HttpPost("/login")]
    public async Task<IActionResult> Login([FromBody] User? user)
    {
        var (login, password) = (user?.Login, user?.Password);
        if(string.IsNullOrEmpty(login = login?.Trim()) || string.IsNullOrEmpty(password))
            return StatusCode(403);

        user = await UserProfile.Find(login.ToUserId(), HttpContext.RequestAborted);
        if(user == null || !PasswordHelper.IsPasswordCorrect(password, user.Salt!, user.PasswordHash!, Key))
            return StatusCode(403);

        Response.SetAuth(user.Login!, Key);
        return Ok(user);
    }

    [HttpGet("/file/{fileId}")]
    public async Task<IActionResult> GetFile(Guid fileId, bool export)
    {
        var userId = Request.Auth(Key);
        if(userId == null)
            return StatusCode(401);

        var stream = UserProfile.TryReadFile(userId.Value, fileId);
        if(stream == null)
            return StatusCode(404);

        return export
            ? new FileContentResult(await Converter.ConvertToDocx(stream, stream.Name, HttpContext.RequestAborted), "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {FileDownloadName = fileId + ".docx"}
            : new FileStreamResult(stream, new MediaTypeHeaderValue("text/html")) {FileDownloadName = fileId + ".html"};
    }

    [HttpPut("/file/{fileId}")]
    public async Task<IActionResult> UpdateFile(Guid fileId)
    {
        var userId = Request.Auth(Key);
        if(userId == null)
            return StatusCode(401);

        await using var stream = UserProfile.TryUpdateFile(userId.Value, fileId);
        if(stream == null)
            return StatusCode(429);

        await stream.WriteAsync(Encoding.UTF8.GetBytes("<html><body>"));
        await using var input = Request.BodyReader.AsStream();
        await input.CopyToAsync(stream, HttpContext.RequestAborted);
        await stream.WriteAsync(Encoding.UTF8.GetBytes("</body></html>"));

        return Ok();
    }

    [HttpGet("/files")]
    public IActionResult ListFiles()
    {
        var userId = Request.Auth(Key);
        if(userId == null)
            return StatusCode(401);

        return Ok(UserProfile.ListFiles(userId.Value));
    }

    private byte[] Key => config.GetValue<byte[]>("key");

    private readonly IConfiguration config;
}
