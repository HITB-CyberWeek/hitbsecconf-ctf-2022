using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace checker.rnd
{
	internal static class RndUtil
	{
		public static bool DebugZeroDelays = false;

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static T Choice<T>(params T[] array) => array[ThreadStaticRnd.Next(array.Length)];

		public static T OrDefaultWithProbability<T>(this T item, double probability) => GetDouble() > probability ? item : default;

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static char Choice(string str) => str[ThreadStaticRnd.Next(str.Length)];

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static int GetInt(int inclusiveMinValue, int exclusiveMaxValue) => ThreadStaticRnd.Next(inclusiveMinValue, exclusiveMaxValue);

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static double GetDouble() => ThreadStaticRnd.NextDouble();

		[MethodImpl(MethodImplOptions.AggressiveInlining)]
		public static DateTime GetDateTime() => new(ThreadStaticRnd.NextInt64(0L, DateTime.MaxValue.Ticks));

		public static bool Bool() => ThreadStaticRnd.Next(2) == 0;

		public static Random ThreadStaticRnd => rnd ??= new Random(Guid.NewGuid().GetHashCode());

		public static Task RndDelay(int max) => DebugZeroDelays ? Task.CompletedTask : Task.Delay(ThreadStaticRnd.Next(max));
		public static Task RndDelay(int max, ref int total)
		{
			if (DebugZeroDelays)
				return Task.CompletedTask;

			var delay = ThreadStaticRnd.Next(max);
			total += delay;

			return Task.Delay(delay);
		}

		public static IEnumerable<T> RandomOrder<T>(this IEnumerable<T> enumerable)
			=> enumerable.OrderBy(_ => ThreadStaticRnd.Next()).Select(item => item);

		[ThreadStatic] private static Random rnd;
	}
}
