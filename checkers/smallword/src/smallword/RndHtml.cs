using System;
using System.IO;
using System.Net;
using System.Text;
using checker.rnd;

namespace checker.smallword;

public static class RndHtml
{
    public static string Generate(string flag, out string b64img)
        => new StringBuilder()
            .RndHeader()
            .RndParagraph()
            .Append("<hr />")
            .AddText(flag)
            .Append("<hr />")
            .RndParagraph()
            .RndHeader()
            .RndImg(out b64img)
            .RndParagraph()
            .RndParagraph()
            .ToString();

    private static StringBuilder AddText(this StringBuilder builder, string text)
        => builder.Append("<p").Append(RandomStyle()).Append('>').Append(WebUtility.HtmlEncode(text)).Append("</p>");

    private static StringBuilder RndHeader(this StringBuilder builder)
    {
        var tag = RndUtil.Choice(HeadersTags);
        return builder.Append('<').Append(tag).Append(RandomStyle()).Append('>').Append(WebUtility.HtmlEncode(RndText.RandomText(RndUtil.GetInt(3, 30)))).Append("</").Append(tag).Append('>');
    }

    private static StringBuilder RndParagraph(this StringBuilder builder)
        => builder.Append("<p>").Append(WebUtility.HtmlEncode(RndText.RandomText(RndUtil.GetInt(3, 200)).RandomUmlauts())).Append("</p>");

    private static StringBuilder RndImg(this StringBuilder builder, out string b64img)
    {
        var ms = new MemoryStream();
        var size = RndUtil.GetInt(32, 65);
        RndImage.Generate(size, size, ms, out var format);
        return builder.Append("<img src=\"data:image/").Append(format).Append(";base64,").Append(b64img = Convert.ToBase64String(new Span<byte>(ms.GetBuffer(), 0, (int)ms.Position))).Append("\" />");
    }

    private static string RandomStyle()
        => $" style=\"{RandomCssTextAlign().OrDefaultWithProbability(0.8)}{RandomCssColor().OrDefaultWithProbability(0.8)}{RandomCssBkColor().OrDefaultWithProbability(0.8)}\"";

    private static string RandomCssTextAlign()
        => $"text-align: {RndUtil.Choice("left", "center", "right")};";

    private static string RandomCssColor()
        => $"color: rgb({RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)});";

    private static string RandomCssBkColor()
        => $"background-color: rgb({RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)}, {RndUtil.GetInt(0, 256)});";

    private static string[] HeadersTags = {"h1", "h2", "h3", "h4", "h5", "h6"};
    private static string[] TextFormatTags = {"strong", "em", "s", "sup", "sub"};
}