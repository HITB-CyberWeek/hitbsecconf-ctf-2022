using System;
using System.Collections.Generic;
using System.Text;
using checker.utils;

namespace checker.rnd
{
	internal static class RndText
	{
		private static readonly string[] Bigrams =
		{
			"TH", "OF", "AN", "IN", "TO", "CO", "BE", "HE", "RE", "HA", "WA", "FO", "WH", "MA", "WI", "ON", "HI", "PR", "ST",
			"NO", "IS", "IT", "SE", "WE", "AS", "CA", "DE", "SO", "MO", "SH", "DI", "AL", "AR", "LI", "WO", "FR", "PA", "ME",
			"AT", "SU", "BU", "SA", "FI", "NE", "CH", "PO", "HO", "DO", "OR", "UN", "LO", "EX", "BY", "FA", "LA", "LE", "PE",
			"MI", "SI", "YO", "TR", "BA", "GO", "BO", "GR", "TE", "EN", "OU", "RA", "AC", "FE", "PL", "CL", "SP", "BR", "EV",
			"TA", "DA", "AB", "TI", "RO", "MU", "EA", "NA", "SC", "AD", "GE", "YE", "AF", "AG", "UP", "AP", "DR", "US", "PU",
			"CE", "IF", "RI", "VI", "IM", "AM", "KN", "OP", "CR", "OT", "JU", "QU", "TW", "GA", "VA", "VE", "PI", "GI", "BI",
			"FL", "BL", "EL", "JO", "FU", "HU", "CU", "RU", "OV", "MY", "OB", "KE", "EF", "PH", "CI", "KI", "NI", "SL", "EM",
			"SM", "VO", "MR", "WR", "ES", "DU", "TU", "AU", "NU", "GU", "OW", "SY", "JA", "OC", "EC", "ED", "ID", "JE", "AI",
			"EI", "SK", "OL", "GL", "EQ", "LU", "AV", "SW", "AW", "EY", "TY"
		};

		private static readonly Dictionary<string, (string, string)> Trigrams = new(StringComparer.Ordinal)
		{
			{"TH", ("EAIOR", "EO")},
			{"AN", ("DTYCSGNIOEAK", "DTYSGOEAK")},
			{"IN", ("GTEDSCAIKVUNF", "GTEDSAK")},
			{"IO", ("NUR", "NUR")},
			{"EN", ("TCDSEIGONA", "TDSEGOA")},
			{"TI", ("ONCVMLETSARF", "NCMLETSARF")},
			{"FO", ("RUOL", "RUOL")},
			{"HE", ("RNYSMIALDT", "RNYSMALDT")},
			{"HA", ("TDVNSRPL", "TDNSRL")},
			{"HI", ("SNCMLPGTRE", "SNCMLPGTRE")},
			{"TE", ("RDNSMLECA", "RDNSMLEA")},
			{"AT", ("IETHUOC", "EHO")},
			{"ER", ("ESIANYTVMROLGFC", "ESANYTM")},
			{"AL", ("LSITEUOMKFA", "LSTEF")},
			{"WA", ("SYRTNL", "SYRTNL")},
			{"VE", ("RNLSD", "RNLSD")},
			{"CO", ("NMURLVSO", "NMURLO")},
			{"RE", ("SADNECLTPMVGFQ", "SADNELTPM")},
			{"IT", ("HIYESTAU", "HYESA")},
			{"WI", ("TLNS", "TLNS")},
			{"ME", ("NRDTSMA", "NRDTSMA")},
			{"NC", ("EIHTROL", "EHT")},
			{"ON", ("SETGADLCVOIF", "SETGADO")},
			{"PR", ("OEIA", "EA")},
			{"AR", ("ETDYSIRLMKGAONC", "ETDYSMKAN")},
			{"ES", ("STEIPUC", "STE")},
			{"EV", ("EI", "E")},
			{"ST", ("ARIEOUS", "AEOS")},
			{"EA", ("RSTDLCNVMK", "RSTDLNM")},
			{"IV", ("EIA", "E")},
			{"EC", ("TOIEAURH", "TEH")},
			{"NO", ("TWRUNM", "TWRUNM")},
			{"OU", ("TLRNSGPB", "TLRNSP")},
			{"PE", ("RNCADTO", "RNADT")},
			{"IL", ("LEIYDA", "LEYD")},
			{"IS", ("THSIECM", "THSEM")},
			{"MA", ("NTLKDSIG", "NTLDS")},
			{"AV", ("EIA", "E")},
			{"OM", ("EPMIA", "E")},
			{"IC", ("AHEITKUS", "HETKS")},
			{"GH", ("T", "T")},
			{"DE", ("RNSDAVPTMLF", "RNSDAPTML")},
			{"AI", ("NDRLT", "NDRLT")},
			{"CT", ("IEUSO", "ESO")},
			{"IG", ("HNI", "HN")},
			{"ID", ("E", "E")},
			{"OR", ("ETMDSKIYLGARNC", "ETMDSKYAN")},
			{"OV", ("EI", "E")},
			{"UL", ("DTAL", "DTL")},
			{"YO", ("U", "U")},
			{"BU", ("TSRI", "TSR")},
			{"RA", ("TNLCIMDSRPGB", "TNLMDSR")},
			{"FR", ("OEA", "EA")},
			{"RO", ("MUVPNWSOLDCBATG", "MUPNWOLDT")},
			{"WH", ("IEOA", "EO")},
			{"OT", ("HETI", "HE")},
			{"BL", ("EIYOA", "EY")},
			{"NT", ("EISROALYUH", "ESOAYH")},
			{"UN", ("DTICG", "DTG")},
			{"TR", ("AIOEUY", "AEY")},
			{"HO", ("UWSRLOMTPND", "UWRLOMTPND")},
			{"AC", ("TEKHCRI", "TEKH")},
			{"TU", ("RDAT", "RT")},
			{"WE", ("RLEVSNA", "RLESNA")},
			{"CA", ("LNTRUSMP", "LNTRSM")},
			{"SH", ("EOIA", "EO")},
			{"UR", ("ENTSIAYRPC", "ENTSAY")},
			{"IE", ("SNDTWVRLF", "SNDTWRL")},
			{"PA", ("RTSNLIC", "RTSNL")},
			{"TO", ("RONWPML", "RONWPML")},
			{"EE", ("NDTMSRPLK", "NDTMSRPLK")},
			{"LI", ("NTSCKGEFZVOMA", "NTSCGEFMA")},
			{"RI", ("NECTSGAVOPMLDB", "NECTSGAPMLD")},
			{"UG", ("HG", "H")},
			{"AM", ("EPIOA", "E")},
			{"ND", ("EISAUO", "ESO")},
			{"US", ("ETISLH", "ETSH")},
			{"LL", ("YEOISA", "YES")},
			{"AS", ("TSEIUOKH", "TSEOH")},
			{"TA", ("TNLIRKBGC", "TNLR")},
			{"LE", ("SDATCRNMGVF", "SDATRNM")},
			{"MO", ("RSVTUD", "RTUD")},
			{"WO", ("RU", "RU")},
			{"MI", ("NLSTCG", "NLSTCG")},
			{"AB", ("LOI", "")},
			{"EL", ("LYIEFOATSPD", "LYEFTSD")},
			{"IA", ("LNT", "LNT")},
			{"NA", ("LTRNM", "LTRNM")},
			{"SS", ("IEUOA", "EO")},
			{"AG", ("EAO", "EO")},
			{"TT", ("ELI", "E")},
			{"NE", ("DSWREYVTLCA", "DSWREYTLA")},
			{"PL", ("AEIYO", "EY")},
			{"LA", ("TNRSCYWIB", "TNRSYW")},
			{"OS", ("TESI", "TES")},
			{"CE", ("SNRDPLI", "SNRDPL")},
			{"DI", ("SNTDFECAVR", "SNTDFECAR")},
			{"BE", ("RECTLFSIGDA", "RETLSDA")},
			{"AP", ("PEA", "E")},
			{"SI", ("ONDTSGCBVMA", "NDTSGCMA")},
			{"NI", ("NTSCZOGF", "NTSCGF")},
			{"OW", ("NESIA", "NES")},
			{"SO", ("NMULCR", "NMULR")},
			{"AK", ("EI", "E")},
			{"CH", ("EAIOUR", "EO")},
			{"EM", ("ESPOBAI", "ES")},
			{"IM", ("EPIASM", "ES")},
			{"SE", ("DNLSRECTVA", "DNLSRETA")},
			{"NS", ("TIE", "TE")},
			{"PO", ("SRNLWTI", "RNLWT")},
			{"EI", ("RNGT", "RNGT")},
			{"EX", ("PTICA", "T")},
			{"KI", ("N", "N")},
			{"UC", ("HTKE", "HTKE")},
			{"AD", ("EIYVMD", "EY")},
			{"GR", ("EAO", "EA")},
			{"IR", ("ESTLI", "EST")},
			{"NG", ("ESLTRI", "ES")},
			{"OP", ("EPL", "E")},
			{"SP", ("EOIA", "E")},
			{"OL", ("DLIOEU", "DLE")},
			{"DA", ("YTRN", "YTRN")},
			{"NL", ("Y", "Y")},
			{"TL", ("YE", "YE")},
			{"LO", ("WNOSCVUTRPG", "WNOUTRP")},
			{"BO", ("UTRODA", "UTROD")},
			{"RS", ("TEOI", "TEO")},
			{"FE", ("REWLCA", "REWLA")},
			{"FI", ("RNCELG", "RNCELG")},
			{"SU", ("RCPBMLA", "RPML")},
			{"GE", ("NTSRD", "NTSRD")},
			{"MP", ("LOATRE", "TE")},
			{"UA", ("LTR", "LTR")},
			{"OO", ("KDLTRNM", "KDLTRNM")},
			{"RT", ("IHAEYUS", "HAEYS")},
			{"SA", ("IMYNL", "MYNL")},
			{"CR", ("EIOA", "EA")},
			{"FF", ("EI", "E")},
			{"IK", ("E", "E")},
			{"MB", ("E", "E")},
			{"KE", ("DNTSRE", "DNTSRE")},
			{"FA", ("CRMI", "RM")},
			{"CI", ("ATESPN", "ATESPN")},
			{"EQ", ("U", "")},
			{"AF", ("TF", "TF")},
			{"ET", ("TIHEYWSA", "HEYSA")},
			{"AY", ("SE", "S")},
			{"MU", ("SNLC", "SNL")},
			{"UE", ("SN", "SN")},
			{"HR", ("OEI", "E")},
			{"TW", ("OE", "OE")},
			{"GI", ("NVOC", "NC")},
			{"OI", ("N", "N")},
			{"VI", ("NDSCTOLE", "NDSCTLE")},
			{"CU", ("LRTS", "LRTS")},
			{"FU", ("LRN", "LRN")},
			{"ED", ("IUE", "E")},
			{"QU", ("IEA", "E")},
			{"UT", ("IHE", "HE")},
			{"RC", ("HE", "HE")},
			{"OF", ("FT", "FT")},
			{"CL", ("EAUO", "E")},
			{"FT", ("E", "E")},
			{"IZ", ("EA", "E")},
			{"PP", ("EORL", "E")},
			{"RG", ("EA", "E")},
			{"DU", ("CSRA", "SR")},
			{"RM", ("ASIE", "SE")},
			{"YE", ("ASD", "ASD")},
			{"RL", ("YD", "YD")},
			{"DO", ("WNME", "WNM")},
			{"AU", ("TS", "TS")},
			{"EP", ("TOEA", "TE")},
			{"BA", ("SCRNL", "SRNL")},
			{"JU", ("S", "S")},
			{"RD", ("SEI", "SE")},
			{"RU", ("SNC", "SN")},
			{"OG", ("RI", "")},
			{"BR", ("OIEA", "EA")},
			{"EF", ("OFUTE", "FTE")},
			{"KN", ("OE", "OE")},
			{"LS", ("O", "O")},
			{"GA", ("NITR", "NTR")},
			{"PI", ("NTREC", "NTREC")},
			{"YI", ("N", "N")},
			{"BI", ("LTN", "LTN")},
			{"IB", ("LIE", "E")},
			{"UB", ("L", "")},
			{"VA", ("LTRN", "LTRN")},
			{"OC", ("KIECA", "KE")},
			{"IF", ("IFET", "FET")},
			{"RN", ("IEMA", "EA")},
			{"RR", ("IEYO", "EY")},
			{"SC", ("HROIA", "H")},
			{"TC", ("H", "H")},
			{"CK", ("E", "E")},
			{"DG", ("E", "E")},
			{"DR", ("EOIA", "EA")},
			{"MM", ("EUI", "E")},
			{"NN", ("EOI", "EO")},
			{"OD", ("EYU", "EY")},
			{"RV", ("EI", "E")},
			{"UD", ("EI", "E")},
			{"XP", ("E", "E")},
			{"JE", ("C", "")},
			{"UM", ("BE", "E")},
			{"EG", ("ARIE", "E")},
			{"DL", ("YE", "YE")},
			{"PH", ("YOIE", "YOE")},
			{"SL", ("YA", "Y")},
			{"GO", ("VTO", "TO")},
			{"CC", ("UOE", "E")},
			{"LU", ("TSMED", "TSME")},
			{"OA", ("TRD", "TRD")},
			{"PU", ("TRLB", "TRL")},
			{"UI", ("TRL", "TRL")},
			{"YS", ("T", "T")},
			{"ZA", ("T", "T")},
			{"HU", ("SRNM", "SRNM")},
			{"MR", ("S", "S")},
			{"OE", ("S", "S")},
			{"SY", ("S", "S")},
			{"EO", ("RP", "RP")},
			{"TY", ("P", "")},
			{"UP", ("PO", "")},
			{"FL", ("OE", "E")},
			{"LM", ("O", "")},
			{"NF", ("O", "")},
			{"RP", ("O", "")},
			{"OH", ("N", "")},
			{"NU", ("M", "M")},
			{"XA", ("M", "M")},
			{"OB", ("L", "")},
			{"VO", ("L", "L")},
			{"DM", ("I", "")},
			{"GN", ("I", "")},
			{"LD", ("IE", "E")},
			{"PT", ("I", "")},
			{"SK", ("IE", "E")},
			{"WR", ("I", "")},
			{"JO", ("H", "")},
			{"LT", ("HE", "HE")},
			{"YT", ("H", "H")},
			{"UF", ("F", "F")},
			{"BJ", ("E", "")},
			{"DD", ("E", "E")},
			{"EY", ("E", "")},
			{"GG", ("E", "E")},
			{"GL", ("EA", "E")},
			{"GU", ("E", "E")},
			{"HT", ("E", "E")},
			{"LV", ("E", "E")},
			{"MS", ("E", "E")},
			{"NM", ("E", "E")},
			{"NV", ("E", "E")},
			{"OK", ("E", "E")},
			{"PM", ("E", "E")},
			{"RK", ("E", "E")},
			{"SW", ("E", "E")},
			{"TM", ("E", "E")},
			{"XC", ("E", "E")},
			{"ZE", ("D", "D")},
			{"AW", ("A", "")},
			{"SM", ("A", "")}
		};

		public static string RandomText(int n)
		{
			if(n <= 0) return string.Empty;
			var builder = new StringBuilder(n);
			while(builder.Length < n)
			{
				builder.Append(RandomWord(RndUtil.GetInt(2, 10)));
				builder.Append(' ');
			}
			builder.Length = n;
			//builder[0] = char.ToUpper(builder[0]);
			return builder.ToString();
		}

		public static string RandomWord(int n)
		{
			var lookup = new char[2];
			var builder = new StringBuilder(n);
			while(builder.Length < n)
			{
				if(builder.Length < 2)
				{
					builder.Append(RndUtil.Choice(Bigrams));
					continue;
				}

				lookup[0] = builder[^2];
				lookup[1] = builder[^1];

				var bigram = new string(lookup);
				var candidates = builder.Length == n - 1 ? Trigrams.GetOrDefault(bigram).Item2 : Trigrams.GetOrDefault(bigram).Item1;

				if(candidates?.Length > 0)
					builder.Append(RndUtil.Choice(candidates));
				else
					builder.Length = Math.Max(0, builder.Length - 3);
			}
			return builder.ToString().ToLower();
		}

		public static string RandomUpperCase(this string value)
		{
			var chars = value.ToCharArray();
			for(int i = 0; i < chars.Length; i++)
			{
				if(RndUtil.ThreadStaticRnd.Next(4) == 0)
					chars[i] = char.ToUpperInvariant(chars[i]);
			}
			return new string(chars);
		}

		public static string RandomSpecials(this string value)
			=> RandomChangeByDict(value, Specials, 4);
		public static string RandomUmlauts(this string value)
			=> RandomChangeByDict(value, Umlauts, 16);
		public static string RandomLeet(this string value)
			=> RandomChangeByDict(value, Leet, 4);

		public static string RandomChangeByDict(this string value, Dictionary<char, char> dict, int share)
		{
			var chars = value.ToCharArray();
			for(int i = 0; i < chars.Length; i++)
			{
				if(dict.TryGetValue(chars[i], out var c) && RndUtil.ThreadStaticRnd.Next(share) == 0)
					chars[i] = c;
			}
			return new string(chars);
		}

		public static string RandomWhitespaces(this string value)
		{
			var chars = value.ToCharArray();
			for(int i = 0; i < chars.Length; i++)
			{
				if(chars[i] == ' ' && RndUtil.ThreadStaticRnd.Next(8) == 0)
					chars[i] = RndUtil.Choice(Whitespaces);
			}
			return new string(chars);
		}

		private static readonly Dictionary<char, char> Leet = new()
		{
			{'o', '0'},
			{'l', '1'},
			{'e', '3'},
			{'t', '7'},
		};

		private static readonly Dictionary<char, char> Specials = new()
		{
			{'a', '@'},
			{'h', '#'},
			{'s', '$'},
			{'c', '<'},
			{'g', '&'},
			{'1', '!'}
		};

		private static readonly Dictionary<char, char> Umlauts = new()
		{
			{'s', 'ß'},
			{'o', 'ö'},
			{'u', 'ü'},
			{'e', 'ë'},
			{'a', 'â'},
			{'z', 'ž'},
			{'n', 'ň'},
			{'y', 'ý'},
			{'i', 'ï'}
		};

		private static readonly char[] Whitespaces = {' ', '\t', '\u00A0'};
	}
}
