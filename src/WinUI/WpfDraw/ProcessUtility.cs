using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Management;
using System.Text.RegularExpressions;

namespace WpfCommon.Utility
{
    public static class ProcessUtility
    {
        readonly static char[] _separator;
        readonly static Regex _regStart;
        readonly static Regex _regEnd;
        readonly static Process _current;

        static ProcessUtility()
        {
            _separator = new char[] { ' ' };
            _regStart = new Regex("^\"{1}");
            _regEnd = new Regex("\"{1}$");
            _current = Process.GetCurrentProcess();
        }

        public static Process Current
        {
            get { return _current; }
        }

        public static Process GetProcess(Func<Process, bool> searchFunc)
        {
            if (searchFunc == null) { return null; }

            foreach (var process in Process.GetProcesses())
            {
                try
                {
                    if (process == null || process.HasExited)
                    {
                        continue;
                    }

                    if (searchFunc(process)) { return process; }
                }
                catch (Win32Exception) { }
                catch (InvalidOperationException) { }
            }

            return null;
        }

        public static string GetModuleName()
        {
            return GetModuleName(Current.Id);
        }

        public static string GetModuleName(int processId)
        {
            var name = (string)Search(processId, "ExecutablePath");

            return Path.GetFileNameWithoutExtension(name);
        }

        public static string[] GetArguments()
        {
            return GetArguments(Current.Id);
        }

        public static string[] GetArguments(int processId)
        {
            var cmdLine = (string)Search(processId, "CommandLine");

            return SplitCmdLine(cmdLine).ToArray();
        }

        public static uint GetParentProcessId()
        {
            return GetParentProcessId(Current.Id);
        }

        public static uint GetParentProcessId(int processId)
        {
            return (uint)Search(processId, "ParentProcessId");
        }

        public static object Search(int processId, string property)
        {
            var query = string.Format("SELECT {0} FROM Win32_Process WHERE ProcessId = {1}", property, processId);

            using (var search = new ManagementObjectSearcher(@"root\CIMV2", query))
            using (var results = search.Get().GetEnumerator())
            {
                if (!results.MoveNext())
                {
                    throw new ApplicationException(string.Format(CultureInfo.InvariantCulture, "Couldn't Get {0}.", property));
                }

                //クエリから結果を取得
                var queryResult = results.Current;

                return queryResult[property];
            }
        }

        public static object Search(uint processId, string property)
        {
            return Search((int)processId, property);
        }

        private static IEnumerable<string> SplitCmdLine(string cmdLine)
        {
            if (cmdLine.IndexOf("\"") == -1)
            {
                // '"'が含まれていなければ空白区切りの結果をそのまま返す
                return cmdLine.Split(_separator, StringSplitOptions.RemoveEmptyEntries);
            }

            var newCmdLines = new List<string>();
            var separator = _separator[0];

            var combiTemp = string.Empty;
            var dQquotStart = false;

            foreach (var split in cmdLine.Split(_separator))
            {
                var startBit = (_regStart.IsMatch(split) ? 1 : 0);
                var endBit = (_regEnd.IsMatch(split) ? 2 : 0);

                switch ((startBit | endBit))
                {
                case 0:
                    // 先頭, 終端共に'"'がない
                    if (!dQquotStart)
                    {
                        newCmdLines.Add(split);
                    }
                    else
                    {
                        combiTemp += (split + separator);
                    }

                    break;
                case 1:
                    // 先頭に'"'があり、終端に'"'がない
                    combiTemp = split.TrimStart('"') + separator;
                    dQquotStart = true;
                    break;
                case 2:
                    // 先頭に'"'がなく、終端に'"'がある
                    combiTemp += split.TrimEnd('"');
                    newCmdLines.Add(combiTemp);
                    dQquotStart = false;
                    break;
                case 3:
                    // 先頭, 終端共に'"'がある
                    newCmdLines.Add(split.Trim('"'));
                    break;
                }
            }

            // 再連結したリスト中の空文字は除いておく
            return newCmdLines.Where(v => !string.IsNullOrEmpty(v));
        }
    }
}
