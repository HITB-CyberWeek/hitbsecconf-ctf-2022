using System;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using checker.smallword;
using checker.rnd;
using checker.utils;

namespace checker
{
	internal static class Program
	{
		private static async Task<int> Main(string[] args)
		{
			try
			{
				var arguments = ParseArgs(args);
				var checker = new SmallWordChecker();

				await Do(checker, arguments).ConfigureAwait(false);

				return (int)ExitCode.OK;
			}
			catch(Exception e)
			{
				var error = e as CheckerException ?? (e as AggregateException)?.Flatten().InnerExceptions?.OfType<CheckerException>().FirstOrDefault();
				if(error != null)
				{
					if(error.StdOut != null)
					{
						await Console.Error.WriteLineAsync(error.StdOut).ConfigureAwait(false);
						await Console.Out.WriteLineAsync(error.StdOut).ConfigureAwait(false);
					}

					return (int)error.ExitCode;
				}

				await Console.Error.WriteLineAsync(e.ToString()).ConfigureAwait(false);
				return (int)ExitCode.CHECKER_ERROR;
			}
		}

		private static async Task Do(IChecker checker, CheckerArgs args)
		{
			switch(args.Command)
			{
				case Command.Debug:
					await Debug(checker, args.Host).ConfigureAwait(false);
					break;
				case Command.Info:
					await Console.Out.WriteLineAsync(await checker.Info().ConfigureAwait(false)).ConfigureAwait(false);
					break;
				case Command.Check:
					await checker.Check(args.Host).ConfigureAwait(false);
					break;
				case Command.Put:
					var result = await checker.Put(args.Host, args.Id, args.Flag, args.Vuln).ConfigureAwait(false);
					var state = JsonSerializer.Serialize(result, result.GetType(), JsonOptions);
					await Console.Error.WriteLineAsync(state.ShortenLog()).ConfigureAwait(false);
					await Console.Out.WriteLineAsync(state).ConfigureAwait(false);
					break;
				case Command.Get:
					var flagId = JsonSerializer.Deserialize<PutResult>(args.Id, JsonOptions);
					await checker.Get(args.Host, flagId, args.Flag, args.Vuln).ConfigureAwait(false);
					break;
				default:
					throw new CheckerException(ExitCode.CHECKER_ERROR, "Unknown command");
			}
		}

		private static async Task Debug(IChecker checker, string host)
		{
			RndUtil.DebugZeroDelays = true;
			for(int i = 0; i < int.MaxValue; i++)
			{
				try
				{
					var vulns = (await checker.Info().ConfigureAwait(false)).Split('\n').First().Split(':').Skip(1).Select(v => int.Parse(v.Trim())).ToArray();
					await StderrWriteLineColoredAsync("CHECK", ConsoleColor.Yellow).ConfigureAwait(false);
					await checker.Check(host).ConfigureAwait(false);

					var vuln = RndDbg.RandomVuln(vulns);
					var flag = RndDbg.RandomFlag();
					await Console.Error.WriteLineAsync(flag).ConfigureAwait(false);

					await StderrWriteLineColoredAsync("PUT", ConsoleColor.Yellow).ConfigureAwait(false);
					var result = await checker.Put(host, "", flag, vuln).ConfigureAwait(false);
					var serialized = JsonSerializer.Serialize(result, result.GetType(), JsonOptions);
					await Console.Error.WriteLineAsync(serialized).ConfigureAwait(false);
					await StderrWriteLineColoredAsync("GET", ConsoleColor.Yellow).ConfigureAwait(false);
					var deserialized = JsonSerializer.Deserialize<PutResult>(serialized, JsonOptions);
					await checker.Get(host, deserialized, flag, vuln).ConfigureAwait(false);

					await StderrWriteLineColoredAsync(ExitCode.OK.ToString(), ConsoleColor.Green).ConfigureAwait(false);
				}
				catch(CheckerException e)
				{
					await Console.Error.WriteLineAsync($"{e.ExitCode} {e.StdOut}").ConfigureAwait(false);
					return;
				}
			}
		}

		private static CheckerArgs ParseArgs(string[] args)
		{
			if(args.Length == 0)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			if(!Enum.TryParse(args[0], true, out Command command) || !Enum.IsDefined(typeof(Command), command))
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Unknown command");
			if(command == Command.Info)
				return new CheckerArgs {Command = command};
			if(args.Length == 1)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			if(command == Command.Check || command == Command.Debug)
				return new CheckerArgs {Command = command, Host = args[1]};
			if(args.Length < 5)
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Not enough arguments");
			if(!int.TryParse(args[4], out var vuln))
				throw new CheckerException(ExitCode.CHECKER_ERROR, "Invalid vuln");
			return new CheckerArgs {Command = command, Host = args[1], Id = args[2], Flag = args[3], Vuln = vuln};
		}

		private static async Task StderrWriteLineColoredAsync(string line, ConsoleColor color)
		{
			Console.ForegroundColor = color;
			await Console.Error.WriteLineAsync(line).ConfigureAwait(false);
			Console.ResetColor();
		}

		private class CheckerArgs
		{
			public Command Command;
			public string Host;
			public string Id;
			public string Flag;
			public int Vuln;
		}

		private static readonly JsonSerializerOptions JsonOptions = new()
		{
			IncludeFields = true,
			PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
			DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingDefault
		};
	}
}
