using System.Threading.Tasks;

namespace checker
{
	internal interface IChecker
	{
		Task<string> Info();
		Task Check(string host);
		Task<PutResult> Put(string host, string flagId, string flag, int vuln);
		Task Get(string host, PutResult state, string flag, int vuln);
	}
}
