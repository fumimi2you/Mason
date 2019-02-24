using Newtonsoft.Json;
using System.Collections.Generic;

namespace PyDraw
{
    public class xy
    {
        public double x { get; set; }
        public double y{ get; set; }
    };

    public enum EReqCode : int
    {
        eReq_Unknown  = 0,
        eReq_SetImage = 1000,
        eReq_ProcCore = 2000,
        eReq_Close    = -1,
    };

    public enum EResCode : int
    {
        eRes_Success = 0,
        eReq_Warning = 1000,
        eReq_Error   = -1,
    };


    [JsonObject("user")]
    public class PyRequest
    {
        [JsonProperty("reqCode")]
        public EReqCode ReqCode { get; set; } = EReqCode.eReq_Unknown;

        [JsonProperty("sessionID")]
        public string SessionID { get; set; } = string.Empty;

        [JsonProperty("imagePath")]
        public string PathImage { get; set; } = string.Empty;

        [JsonProperty("fixedContours")]
        public List<List<xy>> FixedContours { get; set; } = new List<List<xy>>();

        [JsonProperty("addContourSeeds")]
        public List<List<xy>> AddContourSeeds { get; set; } = new List<List<xy>>();

        [JsonProperty("reductContourSeeds")]
        public List<List<xy>> ReductContourSeeds { get; set; } = new List<List<xy>>();

        public string ToJsonString( bool bFormatting = false) {
            if(bFormatting) return JsonConvert.SerializeObject(this, Formatting.Indented);
            else return JsonConvert.SerializeObject(this);
        }
    }


    /// <summary>
    /// phang解析結果
    /// </summary>
    [JsonObject("user")]
    public class PyResponse
    {
        [JsonProperty("resCode")]
        public EResCode? ReqCode { get; set; } = null;

        [JsonProperty("sessionID")]
        public string SessionID { get; set; } = string.Empty;

        [JsonProperty("contours")]
        public List<List<xy>> Contours { get; set; } = new List<List<xy>>();

        public string ToJsonString(bool bFormatting = false) {
            if (bFormatting) return JsonConvert.SerializeObject(this, Formatting.Indented);
            else return JsonConvert.SerializeObject(this);
        }
    }
}
