using System.Linq;

namespace checker.utils
{
	internal static class StringUtils
	{
		public static string ShortenLog(this string text, int maxLength = MaxTextSizeToLog)
			=> text?.Length > maxLength ? text.Substring(0, maxLength) + "..." : text;

		public static string NullAwareJoin(string delim, params string[] items)
			=> string.Join(delim, items?.Where(item => item != null) ?? Enumerable.Empty<string>());

		private const int MaxTextSizeToLog = 1024;
	}
}
