using System;
using System.Collections.Generic;
using System.Linq;

namespace checker.rnd
{
	internal static class RndHttp
	{
		public static string RndUa() => RndUtil.Choice(UserAgents);

		public static List<KeyValuePair<string, string>> RndDefaultHeaders(Uri baseUri)
			=> new[] { new KeyValuePair<string, string[]>("Host", new[] { baseUri.Authority }) }
				.Concat(RandomDefaultHeaders)
				.RandomOrder()
				.Select(pair => new KeyValuePair<string, string>(pair.Key, RndUtil.Choice(pair.Value)))
				.Where(pair => pair.Value != null)
				.ToList();

		private static readonly string[] UserAgents =
		{
			null, null, null, null, null, null, null, null, null, null, // Increase probability
			"Java1.8.0_201",
			"Wget/1.21.3", "Wget/1.21.2", "Wget/1.21.1",
			"Go-http-client/2.0", "Go-http-client/1.1",
			"Python-urllib/3.1", "Python-urllib/3.0", "Python-urllib/2.7",
			"python-requests/2.28.1", "python-requests/2.27.0", "python-requests/2.23.0", "python-requests/2.22.0", "python-requests/2.21.0",
			"Python/3.9 aiohttp/3.8.1", "Python/3.9 aiohttp/3.7.4", "Python/3.8 aiohttp/3.7.3", "Python/3.7 aiohttp/3.7.2",
			"libwww-perl/6.67", "libwww-perl/6.57", "libwww-perl/6.56", "libwww-perl 5.76",
			"curl/7.84.0", "curl/7.83.1", "curl/7.79.1", "curl/7.79.0", "curl/7.78.0",
			"Mozilla/5.0 (Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
		};

		private static readonly Dictionary<string, string[]> RandomDefaultHeaders = new()
		{
			{"Accept", new[] {null, null, null, "*/*"}},
			//{"Accept-Encoding", new[] {null, null, null, "gzip, deflate"}},
			{"Connection", new[] {null, null, null, "Keep-Alive", "keep-alive"}},
			{"User-Agent", UserAgents}
		};
	}
}
