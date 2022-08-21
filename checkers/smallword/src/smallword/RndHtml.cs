using System.Net;
using System.Text;

namespace checker.smallword;

public static class RndHtml
{
    public static byte[] Generate(string flag)
    {
        //TODO
        return Encoding.UTF8.GetBytes($"<p>{WebUtility.HtmlEncode(flag)}</p>");
    }
}