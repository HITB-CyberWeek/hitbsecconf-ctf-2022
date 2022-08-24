using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using System.Xml;
using checker.net;
using checker.rnd;
using checker.utils;

namespace checker.smallword
{
	internal class SmallWordChecker : IChecker
	{
		public Task<string> Info() => Task.FromResult("vulns: 1\npublic_flag_description: Flag ID is FILEID@LOGIN, flag is inside file\n");

		public async Task Check(string host)
		{
			var baseUri = GetBaseUri(host);

			int slept = 0;
			await RndUtil.RndDelay(MaxOneTimeDelay, ref slept).ConfigureAwait(false);

			var randomDefaultHeaders = RndHttp.RndDefaultHeaders(baseUri);
			await Console.Error.WriteLineAsync($"random headers '{JsonSerializer.Serialize(new FakeDictionary<string, string>(randomDefaultHeaders))}'").ConfigureAwait(false);
			var client = new AsyncHttpClient(baseUri, randomDefaultHeaders, cookies: false);

			var result = await client.DoRequestAsync(HttpMethod.Get, "/", null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"get / failed: {result.StatusCode.ToReadableCode()}");

			var html = result.BodyAsString.TrimStart();
			if(!(html.StartsWith("<!doctype html", StringComparison.OrdinalIgnoreCase) || html.StartsWith("<html", StringComparison.OrdinalIgnoreCase)))
				throw new CheckerException(ExitCode.MUMBLE, "invalid / response: html expected");

			await Console.Error.WriteLineAsync($"total sleep: {slept} msec").ConfigureAwait(false);
		}

		public async Task<PutResult> Put(string host, string flagId, string flag, int vuln)
		{
			var baseUri = GetBaseUri(host);

			int slept = 0;
			await RndUtil.RndDelay(MaxOneTimeDelay, ref slept).ConfigureAwait(false);

			var randomDefaultHeaders = RndHttp.RndDefaultHeaders(baseUri);
			await Console.Error.WriteLineAsync($"random headers '{JsonSerializer.Serialize(new FakeDictionary<string, string>(randomDefaultHeaders))}'").ConfigureAwait(false);
			var client = new AsyncHttpClient(baseUri, randomDefaultHeaders, cookies: true);

			var user = new User
			{
				BirthDate = ((DateTime?)RndUtil.GetDateTime()).OrDefaultWithProbability(0.8),
				Gender = RndUtil.Choice("male", "female", "cat", RndText.RandomWord(RndUtil.GetInt(2, 10))).OrDefaultWithProbability(0.8),
				Country = RndText.RandomWord(RndUtil.GetInt(2, 10)).OrDefaultWithProbability(0.8),
				Company = RndText.RandomText(RndUtil.GetInt(3, 30)).RandomLeet().RandomSpecials().RandomUmlauts().RandomUpperCase().RandomWhitespaces().OrDefaultWithProbability(0.8),
				Address = RndText.RandomText(RndUtil.GetInt(3, 100)).RandomSpecials().RandomUmlauts().RandomUpperCase().RandomWhitespaces().OrDefaultWithProbability(0.8),
				Name = RndText.RandomText(RndUtil.GetInt(3, 100)).RandomSpecials().RandomUmlauts().RandomUpperCase().RandomWhitespaces().OrDefaultWithProbability(0.8),
				Surname = RndText.RandomText(RndUtil.GetInt(3, 100)).RandomSpecials().RandomUmlauts().RandomUpperCase().RandomWhitespaces().OrDefaultWithProbability(0.8),
				Patronymic = RndText.RandomText(RndUtil.GetInt(3, 100)).RandomSpecials().RandomUmlauts().RandomUpperCase().RandomWhitespaces().OrDefaultWithProbability(0.8),

				Login = RndText.RandomWord(RndUtil.GetInt(10, 32)).RandomLeet().RandomUpperCase(),
				Password = RndText.RandomText(RndUtil.GetInt(8, 48)).RandomSpecials().RandomLeet().RandomUmlauts().RandomUpperCase(),

				Hobby = RndText.RandomText(RndUtil.GetInt(3, 300)).RandomSpecials().RandomLeet().RandomUmlauts().RandomWhitespaces().OrDefaultWithProbability(0.8)
			};

			await Console.Error.WriteLineAsync($"user '{JsonSerializer.Serialize(user, JsonOptions)}'").ConfigureAwait(false);

			var data = JsonSerializer.SerializeToUtf8Bytes(user, JsonOptions);
			var result = await client.DoRequestAsync(HttpMethod.Post, ApiRegister, new Dictionary<string, string> {{"Content-Type", "application/json"}}, data, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiRegister} failed: {result.StatusCode.ToReadableCode()}");

			var registered = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<User>(result.BodyAsString, JsonOptions));
			if(registered == null || registered.BirthDate != user.BirthDate || registered.Gender != user.Gender || registered.Country != user.Country || registered.Company != user.Company || registered.Address != user.Address || registered.Name != user.Name || registered.Surname != user.Surname || registered.Patronymic != user.Patronymic || registered.Login != user.Login || registered.Hobby != user.Hobby)
				throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiRegister} response: invalid user returned");

			await Console.Error.WriteLineAsync($"signed up as '{registered.Login}' password '{registered.Password}'").ConfigureAwait(false);

			await RndUtil.RndDelay(MaxDelay, ref slept).ConfigureAwait(false);

			if(RndUtil.Bool())
			{
				data = JsonSerializer.SerializeToUtf8Bytes(new User {Login = user.Login, Password = user.Password}, JsonOptions); 
				result = await client.DoRequestAsync(HttpMethod.Post, ApiLogin, new Dictionary<string, string> {{"Content-Type", "application/json"}}, data, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiLogin} failed: {result.StatusCode.ToReadableCode()}");

				var logged = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<User>(result.BodyAsString, JsonOptions));
				if(logged == null || logged.BirthDate != user.BirthDate || logged.Gender != user.Gender || logged.Country != user.Country || logged.Company != user.Company || logged.Address != user.Address || logged.Name != user.Name || logged.Surname != user.Surname || logged.Patronymic != user.Patronymic || logged.Login != user.Login || logged.Hobby != user.Hobby)
					throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiLogin} response: invalid user returned");

				await Console.Error.WriteLineAsync($"signed in as '{logged.Login}'").ConfigureAwait(false);

				await RndUtil.RndDelay(MaxDelay, ref slept).ConfigureAwait(false);
			}

			var fileId = Guid.NewGuid();
			var stopwatch = Stopwatch.StartNew();
			var html = Encoding.UTF8.GetBytes(RndHtml.Generate(flag, out var image));
			await Console.Error.WriteLineAsync($"html with char size '{html.Length}' generated in '{stopwatch.Elapsed}'").ConfigureAwait(false);

			//TODO: multiple files?

			result = await client.DoRequestAsync(HttpMethod.Put, string.Format(ApiFileFormat, fileId), null, html, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
			if(result.StatusCode != HttpStatusCode.OK)
				throw new CheckerException(result.StatusCode.ToExitCode(), $"put {ApiFileFormat} failed: {result.StatusCode.ToReadableCode()}");

			var cookie = client.Cookies?.GetCookieHeader(baseUri);
			await Console.Error.WriteLineAsync($"cookie '{cookie.ShortenLog(MaxCookieSize)}' with length '{cookie?.Length ?? 0}'").ConfigureAwait(false);

			if(cookie == null || cookie.Length > MaxCookieSize)
				throw new CheckerException(ExitCode.MUMBLE, "too large or invalid cookies");

			var decoded = DoIt.TryOrDefault(() => WebUtility.UrlDecode(cookie));
			if(decoded == null || !decoded.StartsWith($"auth={user.Login} ", StringComparison.Ordinal))
				throw new CheckerException(ExitCode.MUMBLE, "invalid auth cookie format");

			var bytes = DoIt.TryOrDefault(() => Encoding.UTF8.GetBytes(cookie));
			if(bytes == null || bytes.Length > MaxCookieSize)
				throw new CheckerException(ExitCode.MUMBLE, "too large or invalid cookies");

			await Console.Error.WriteLineAsync($"total sleep: {slept} msec").ConfigureAwait(false);

			return new PutResult
			{
				User = user,
				FileId = fileId,
				Base64Image = image,
				Cookie = Convert.ToBase64String(bytes),

				PublicFlagId = $"{fileId}@{user.Login}"
			};
		}

		public async Task Get(string host, PutResult put, string flag, int vuln)
		{
			var baseUri = GetBaseUri(host);

			var user = put.User;
			var fileId = put.FileId;
			var cookie = Encoding.UTF8.GetString(Convert.FromBase64String(put.Cookie));

			HttpResult result;

			int slept = 0;
			await RndUtil.RndDelay(MaxOneTimeDelay, ref slept).ConfigureAwait(false);

			var randomDefaultHeaders = RndHttp.RndDefaultHeaders(baseUri);
			await Console.Error.WriteLineAsync($"random headers '{JsonSerializer.Serialize(new FakeDictionary<string, string>(randomDefaultHeaders))}'").ConfigureAwait(false);
			var client = new AsyncHttpClient(baseUri, randomDefaultHeaders, cookies: true);

			if(RndUtil.Bool())
			{
				await Console.Error.WriteLineAsync($"use saved cookie '{cookie}'").ConfigureAwait(false);
				client.Cookies.SetCookies(baseUri, cookie);
			}
			else
			{
				await Console.Error.WriteLineAsync($"use saved login '{user.Login}' and password '{user.Password}'").ConfigureAwait(false);

				var data = JsonSerializer.SerializeToUtf8Bytes(new User {Login = user.Login, Password = user.Password}, JsonOptions); 
				result = await client.DoRequestAsync(HttpMethod.Post, ApiLogin, new Dictionary<string, string> {{"Content-Type", "application/json"}}, data, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode == HttpStatusCode.Forbidden)
					throw new CheckerException(ExitCode.CORRUPT, $"post {ApiLogin} failed: forbidden");
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"post {ApiLogin} failed: {result.StatusCode.ToReadableCode()}");

				var logged = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<User>(result.BodyAsString, JsonOptions));
				if(logged == null || logged.BirthDate != user.BirthDate || logged.Gender != user.Gender || logged.Country != user.Country || logged.Company != user.Company || logged.Address != user.Address || logged.Name != user.Name || logged.Surname != user.Surname || logged.Patronymic != user.Patronymic || logged.Login != user.Login || logged.Hobby != user.Hobby)
					throw new CheckerException(ExitCode.MUMBLE, $"invalid {ApiLogin} response: invalid user returned");

				await Console.Error.WriteLineAsync($"signed in as '{logged.Login}'").ConfigureAwait(false);

				await RndUtil.RndDelay(MaxDelay, ref slept).ConfigureAwait(false);
			}

			if(RndUtil.Bool())
			{
				result = await client.DoRequestAsync(HttpMethod.Get, ApiList, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode == HttpStatusCode.Unauthorized || result.StatusCode == HttpStatusCode.NotFound)
					throw new CheckerException(ExitCode.CORRUPT, $"get {ApiList} failed: {result.StatusCode.ToReadableCode()}");
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"get {ApiList} failed: {result.StatusCode.ToReadableCode()}");

				var list = DoIt.TryOrDefault(() => JsonSerializer.Deserialize<string[]>(result.BodyAsString, JsonOptions));
				if(list == null || list.Length == 0 || !list.Any(item => item.Contains(fileId.ToString())))
					throw new CheckerException(ExitCode.CORRUPT, $"invalid {ApiList} response: file not found");

				await RndUtil.RndDelay(MaxDelay, ref slept).ConfigureAwait(false);
			}

			if(RndUtil.Bool())
			{
				var relative = string.Format(ApiFileFormat, fileId);
				result = await client.DoRequestAsync(HttpMethod.Get, relative, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode == HttpStatusCode.Unauthorized || result.StatusCode == HttpStatusCode.NotFound)
					throw new CheckerException(ExitCode.CORRUPT, $"get {relative} failed: {result.StatusCode.ToReadableCode()}");
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"get {relative} failed: {result.StatusCode.ToReadableCode()}");

				if(!result.BodyAsString.Contains(flag))
					throw new CheckerException(ExitCode.CORRUPT, $"invalid {relative} response: flag not found");
			}
			else
			{
				var relative = string.Format(ApiFileFormat, fileId) + "?export=true";
				result = await client.DoRequestAsync(HttpMethod.Get, relative, null, null, NetworkOpTimeout, MaxHttpBodySize).ConfigureAwait(false);
				if(result.StatusCode == HttpStatusCode.Unauthorized || result.StatusCode == HttpStatusCode.NotFound)
					throw new CheckerException(ExitCode.CORRUPT, $"get {relative} failed: {result.StatusCode.ToReadableCode()}");
				if(result.StatusCode != HttpStatusCode.OK)
					throw new CheckerException(result.StatusCode.ToExitCode(), $"get {relative} failed: {result.StatusCode.ToReadableCode()}");

				var image = put.Base64Image == null ? null : new MemoryStream(Convert.FromBase64String(put.Base64Image));

				var flagFound = false;
				var imageFound = image == null;

				void CheckXml(Stream stream) => ExtractTextFromXml(stream).ForEach(text => flagFound |= text.Contains(flag));
				void CheckImg(Stream stream) => imageFound |= ImageHelper.Equals(image, stream);

				if(!await DocxTraverse(result.Body, CheckXml, CheckImg).ConfigureAwait(false))
					throw new CheckerException(ExitCode.MUMBLE, $"invalid {relative} response: failed to open docx");
				if(!flagFound)
					throw new CheckerException(ExitCode.CORRUPT, $"invalid {relative} response: flag not found");
				if(!imageFound)
					throw new CheckerException(ExitCode.MUMBLE, $"invalid {relative} response: some content not found in docx");
			}

			await Console.Error.WriteLineAsync($"total sleep: {slept} msec").ConfigureAwait(false);
		}

		// NOTE: This code is focused on a well-defined docx generated by the service, not some generic docx files
		private static async Task<bool> DocxTraverse(Stream stream, Action<Stream> doWithXml, Action<Stream> doWithImage)
		{
			try
			{
				using var archive = new ZipArchive(stream, ZipArchiveMode.Read);
				foreach(var entry in archive.Entries)
				{
					if(entry.FullName.StartsWith("media/", StringComparison.OrdinalIgnoreCase) && (entry.FullName.EndsWith(".png", StringComparison.OrdinalIgnoreCase) || entry.FullName.EndsWith(".jpg", StringComparison.OrdinalIgnoreCase) || entry.FullName.EndsWith(".jpeg", StringComparison.OrdinalIgnoreCase) || entry.FullName.EndsWith(".bmp", StringComparison.OrdinalIgnoreCase)))
						doWithImage(entry.Open());
					if(StringComparer.OrdinalIgnoreCase.Equals(entry.FullName, "word/document.xml") || StringComparer.OrdinalIgnoreCase.Equals(entry.FullName, "word/sharedStrings.xml") || StringComparer.OrdinalIgnoreCase.Equals(entry.FullName, "word/content.xml"))
						doWithXml(entry.Open());
				}
				return true;
			}
			catch(Exception e)
			{
				await Console.Error.WriteLineAsync($"failed to open docx: {e}").ConfigureAwait(false);
				return false;
			}
		}

		private static IEnumerable<string> ExtractTextFromXml(Stream stream)
		{
			using var reader = XmlReader.Create(stream, XmlReaderSettings);
			while(reader.Read())
			{
				if(reader.NodeType == XmlNodeType.Text)
					yield return reader.Value;
			}
		}

		private const int Port = 443;

		private const int MaxHttpBodySize = 64 * 1024;
		private const int MaxCookieSize = 256;

		private const int MaxDelay = 3000;
		private const int MaxOneTimeDelay = 5000;
		private const int NetworkOpTimeout = 12000;

		private static Uri GetBaseUri(string host) => new($"https://{host}:{Port}/");

		private static readonly JsonSerializerOptions JsonOptions = new()
		{
			IncludeFields = true,
			PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
			DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingDefault
		};

		private static readonly XmlReaderSettings XmlReaderSettings = new()
		{
			Async = true,
			CheckCharacters = false,
			XmlResolver = null,
			DtdProcessing = DtdProcessing.Prohibit,
			IgnoreProcessingInstructions = true,
			MaxCharactersFromEntities = 32768,
			MaxCharactersInDocument = 65536
		};

		private const string ApiList = "/files";
		private const string ApiLogin = "/login";
		private const string ApiRegister = "/register";
		private const string ApiFileFormat = "/file/{0}";
	}
}
