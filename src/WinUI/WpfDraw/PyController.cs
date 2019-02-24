using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using WpfCommon.Utility;

namespace PyDraw
{
    class PyController
    {
        private Encoding ENC = Encoding.UTF8;

        private const string ipLocalHost = "127.0.0.1";
        private const int portSrvPy = 60033;

        private const int timeOut = 5 * 60 * 1000;

        private const string scriptFileName = "Mason_srv.py";

        private Process procSrvPy = null;
        private string settionID = null;
        private string m_ImgPath = null;

        public PyController()
        {
        }

        private PyResponse Communicate( PyRequest reqData )
        {
            if (procSrvPy == null) { return null; }

            try
            {
                var mStream = new MemoryStream();
                using (var tcpClient = new TcpClient(ipLocalHost, portSrvPy))
                using (var nStream = tcpClient.GetStream())
                {
                    nStream.ReadTimeout = timeOut;
                    nStream.WriteTimeout = timeOut;

                    var sendMsg = reqData.ToJsonString(false);
                    var sendBytes = ENC.GetBytes(sendMsg);

                    Console.Write("Send : \n{0}\n", sendMsg);
                    nStream.Write(sendBytes, 0, sendBytes.Length);

                    var resSize = 0;
                    var resBytes = new byte[65536];
                    do
                    {
                        resSize = nStream.Read(resBytes, 0, resBytes.Length);
                        if (resSize == 0)
                        {
                            return null;
                        }

                        mStream.Write(resBytes, 0, resSize);
                    } while (nStream.DataAvailable);
                }

                var resMsg = ENC.GetString(mStream.GetBuffer(), 0, (int)mStream.Length);
                Console.Write("Responce : \n{0}\n", resMsg);
                return JsonConvert.DeserializeObject<PyResponse>(resMsg);
            }
            catch(Exception)
            {
                return null;
            }

        }

        public int PyExistsCheck()
        {
            procSrvPy = null;
            var validProc = (from proc in Process.GetProcessesByName("python")
                             where ProcessUtility.GetArguments(proc.Id).Any(v => string.Compare(Path.GetFileName(v), scriptFileName, true) == 0)
                             select proc).ToList();
            if (validProc.Count == 0)
            {
                return -1;
            }
            else
            {
                procSrvPy = validProc[0];
                return procSrvPy.Id;
            }
        }


        public bool SetImage(string imagePath)
        {
            m_ImgPath = imagePath;
            var reqData = new PyRequest()
            {
                ReqCode = EReqCode.eReq_SetImage,
                PathImage = imagePath
            };

            var resData = Communicate(reqData);
            if(resData != null && resData.ReqCode != EResCode.eReq_Error) {
                settionID = resData.SessionID;
                return true;
            } else {
                return false;
            }
        }

        public List<List<OpenCvSharp.Point>> ProcCore(List<List<OpenCvSharp.Point>> fixPointss, List<List<OpenCvSharp.Point>> addPointss, List<List<OpenCvSharp.Point>> subPointss)
        {
            var reqData = new PyRequest()
            {
                ReqCode = EReqCode.eReq_ProcCore,
                SessionID = settionID,
                PathImage = m_ImgPath
            };

            foreach (var points in fixPointss)
            {
                var xyl = new List<xy>();
                foreach (var pt in points) { xyl.Add(new xy() { x = pt.X, y = pt.Y }); }
                reqData.FixedContours.Add(xyl);
            }
            foreach (var points in addPointss)
            {
                var xyl = new List<xy>();
                foreach (var pt in points) { xyl.Add(new xy() { x = pt.X, y = pt.Y }); }
                reqData.AddContourSeeds.Add(xyl);
            }
            foreach (var points in subPointss)
            {
                var xyl = new List<xy>();
                foreach (var pt in points) { xyl.Add(new xy() { x = pt.X, y = pt.Y }); }
                reqData.ReductContourSeeds.Add(xyl);
            }

            var resData = Communicate(reqData);

            var retPtss = new List<List<OpenCvSharp.Point>>();
            if (resData != null && resData.ReqCode != EResCode.eReq_Error)
            {
                foreach (var cont in resData.Contours)
                {
                    var cvCnt = new List<OpenCvSharp.Point>();
                    foreach (var pt in cont)
                    {
                        cvCnt.Add(new OpenCvSharp.Point(pt.x, pt.y));
                    }
                    retPtss.Add(cvCnt);
                }
            }

            return retPtss;
        }

        public bool Close()
        {
            var reqData = new PyRequest()
            {
                ReqCode = EReqCode.eReq_Close,
                SessionID = settionID,
                PathImage = m_ImgPath
            };

            var resData = Communicate(reqData);
            if (resData != null && resData.ReqCode != EResCode.eReq_Error)
            {
                settionID = null;
                return true;
            }
            else
            {
                return false;
            }
        }


    }
}
