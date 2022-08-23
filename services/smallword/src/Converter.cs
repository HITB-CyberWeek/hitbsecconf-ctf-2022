using System.Xml;
using System.Xml.Linq;
using OpenXmlPowerTools;

public static class Converter
{
    public static async Task<byte[]> ConvertToDocx(Stream stream, string filepath, CancellationToken cancellationToken)
    {
        await using var input = stream;
        var html = await ReadAsXElement(input, cancellationToken);

        var settings = HtmlToWmlConverter.GetDefaultSettings();
        settings.BaseUriForImages = Path.GetDirectoryName(filepath);

        var doc = HtmlToWmlConverter.ConvertHtmlToWml(DefaultCss, string.Empty, string.Empty, html, settings, null, null);
        GC.KeepAlive(input);

        return doc.DocumentByteArray;
    }

    private static async Task<XElement> ReadAsXElement(Stream stream, CancellationToken cancellationToken)
    {
        /*var context = new XmlParserContext(null, null, null, XmlSpace.None)
        {
            DocTypeName = "html",
            PublicId = "-//W3C//DTD XHTML 1.0 Strict//EN",
            SystemId = "xhtml1-strict.dtd"
        };*/
        using var reader = XmlReader.Create(stream, XmlReaderSettings);
        return (XElement)RemoveNamespaces(await XElement.LoadAsync(reader, LoadOptions.PreserveWhitespace, cancellationToken));
    }

    private static XNode RemoveNamespaces(XNode node, int depth = 0)
        => node is not XElement element ? node : depth >= 64 ? throw new Exception("Recursion limit exceeded") : new XElement(element.Name.LocalName, element.Attributes().Where(a => !a.IsNamespaceDeclaration), element.Nodes().Select(n => RemoveNamespaces(n, depth + 1)));

    private static readonly XmlReaderSettings XmlReaderSettings = new()
    {
        Async = true,
        CheckCharacters = false,
        XmlResolver = null, //new XmlPreloadedResolver(XmlKnownDtds.Xhtml10),
        DtdProcessing = DtdProcessing.Prohibit,
        IgnoreProcessingInstructions = true,
        MaxCharactersFromEntities = 16384,
        MaxCharactersInDocument = 32768
    };

    private const string DefaultCss =
        @"html, address,
blockquote,
body, dd, div,
dl, dt, fieldset, form,
frame, frameset,
h1, h2, h3, h4,
h5, h6, noframes,
ol, p, ul, center,
dir, hr, menu, pre { display: block; unicode-bidi: embed }
li { display: list-item }
head { display: none }
table { display: table }
tr { display: table-row }
thead { display: table-header-group }
tbody { display: table-row-group }
tfoot { display: table-footer-group }
col { display: table-column }
colgroup { display: table-column-group }
td, th { display: table-cell }
caption { display: table-caption }
th { font-weight: bolder; text-align: center }
caption { text-align: center }
body { margin: auto; }
h1 { font-size: 2em; margin: auto; }
h2 { font-size: 1.5em; margin: auto; }
h3 { font-size: 1.17em; margin: auto; }
h4, p,
blockquote, ul,
fieldset, form,
ol, dl, dir,
menu { margin: auto }
a { color: blue; }
h5 { font-size: .83em; margin: auto }
h6 { font-size: .75em; margin: auto }
h1, h2, h3, h4,
h5, h6, b,
strong { font-weight: bolder }
blockquote { margin-left: 40px; margin-right: 40px }
i, cite, em,
var, address { font-style: italic }
pre, tt, code,
kbd, samp { font-family: monospace }
pre { white-space: pre }
button, textarea,
input, select { display: inline-block }
big { font-size: 1.17em }
small, sub, sup { font-size: .83em }
sub { vertical-align: sub }
sup { vertical-align: super }
table { border-spacing: 2px; }
thead, tbody,
tfoot { vertical-align: middle }
td, th, tr { vertical-align: inherit }
s, strike, del { text-decoration: line-through }
hr { border: 1px inset }
ol, ul, dir,
menu, dd { margin-left: 40px }
ol { list-style-type: decimal }
ol ul, ul ol,
ul ul, ol ol { margin-top: 0; margin-bottom: 0 }
u, ins { text-decoration: underline }
br:before { content: ""\A""; white-space: pre-line }
center { text-align: center }
:link, :visited { text-decoration: underline }
:focus { outline: thin dotted invert }
/* Begin bidirectionality settings (do not change) */
BDO[DIR=""ltr""] { direction: ltr; unicode-bidi: bidi-override }
BDO[DIR=""rtl""] { direction: rtl; unicode-bidi: bidi-override }
*[DIR=""ltr""] { direction: ltr; unicode-bidi: embed }
*[DIR=""rtl""] { direction: rtl; unicode-bidi: embed }
";
}
