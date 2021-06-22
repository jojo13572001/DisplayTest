using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SocketIOClient;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading.Tasks;

namespace DisplayDesktopApp
{
	// https://viewsonic-ssi.visualstudio.com/Display%20App/_wiki/wikis/Display-App.wiki/551/Display-API
	class DisplayAPI
	{
		#region constant
		// STAGE
		private static readonly string CodeMappingEndpoint_STAGE = DisplayFlow.GetEnvironmentVariable("CodeMappingEndpoint_STAGE", 
																									  "https://conn-stage.myviewboard.cloud/display");
		private static readonly string InstanceBindingEndpoint_STAGE = "https://conn-stage.myviewboard.cloud/binding/items";
		private static readonly string ControlSignalEndpoint_STAGE = DisplayFlow.GetEnvironmentVariable("ControlSignalEndpoint_STAGE", 
																										"https://mrtc.stage.myviewboard.cloud");
		// PRODUCTION
		private static readonly string CodeMappingEndpoint_PRODUCTION = "https://conn.myviewboard.cloud/display";
		private static readonly string InstanceBindingEndpoint_PRODUCTION = "https://conn.myviewboard.cloud/signaling/items";
		private static readonly string ControlSignalEndpoint_PRODUCTION = "https://control-io.myviewboard.cloud/";
		// misc
		private static readonly string ICE_QUERY_URL = "https://getice.myviewboard.cloud/";
		private static readonly string RegisterDisplayCode_PATH = "displays"; // POST 
		private static readonly string GetDisplayCodeByDeviceId_PATH= "displays"; // GET 
		private static readonly string GetOTP_PATH = "code"; // GET 
		#endregion

		// Use Stage settings by default..
		private string CodeMappingEndpoint = CodeMappingEndpoint_STAGE;
		private string InstanceBindingEndpoint = InstanceBindingEndpoint_STAGE;
		private string ControlSignalEndpoint = ControlSignalEndpoint_STAGE;

		#region socketio realted
		private string m_DeviceId = "";
		private SocketIO m_ControlSignaling = null;
		private SocketIO m_InstanceBindingSignaling = null;
		private static Random m_Random = new Random();
		#endregion

		#region public
		public class IceServerInfo
		{
			public string url = null;
			public string username = null;
			public string credential = null;
		}
		public class IceServerQueryResult
		{
			public IList<IceServerInfo> list = null;
		}
		#endregion

		#region internal request/reply
		internal struct RegisterDisplayCodeRequest
		{
			public string deviceId { get; set; }
			public Dictionary<string, string> property { get; set; }
		}
		internal struct RegisterDisplayCodeReply
		{
			public string code { get; set; }
			public Dictionary<string, string> property { get; set; }
			public string id { get; set; }
			public string createdAt { get; set; }
			public string updatedAt { get; set; }
		}
		internal struct GetDisplayCodeByDeviceIdReply
		{
			public string code { get; set; }
			public Dictionary<string, string> property { get; set; }
			public string id { get; set; }
			public string createdAt { get; set; }
			public string updatedAt { get; set; }
		}
		internal struct ControlConnectReply
		{
			public string messageFor;
			public string action;
			public string display;
			public string streamer;
			public List<string> capacities;
		}
		internal struct GetStatReportReply
		{
			public string messageFor;
			public string action;
			public string display;
			public string statreport;
			public List<string> capacities;
		}
		internal struct InstanceBindingOnConnectReply
		{
			public string messageFor;
			public string action;
			public string status;
			public string guestId;
			public string direction;
			public bool login;
			public Dictionary<string, object> extra;
		}
		internal struct InstanceBindingSetClientReply
		{
			public string messageFor;
			public string action;
			public Dictionary<string, object> status;
			public Dictionary<string, object> extra;
			public string direction;
			public string messageId;
			public string nextId;
		}
		internal struct InstanceBindingOnUnpublishReply
		{
			public string messageFor;
			public string action;
			public string display;
		}
		internal struct RestfulAPIResult
		{
			public bool ok;
			public int statusCode;
			public string webResponse;
		}
		#endregion

		// Restful API callback
		public event OnGetOTPHandler OnGetOTP = null;
		public delegate void OnGetOTPHandler(string otp);
		public event OnGetDisplayCodeHandler OnGetDisplayCode = null;
		public delegate void OnGetDisplayCodeHandler(string displayCode);
		public event OnRegisterDisplayCodeHandler OnRegisterDisplayCode = null;
		public delegate void OnRegisterDisplayCodeHandler(string displayCode);

		// ControlSignaling SocketIO callback (Issuer: "WebClient" Receiver: "Display")
		public event OnControlConnectRequestHandler OnControlConnectRequest = null;
		public delegate void OnControlConnectRequestHandler(string displayCode, string allowId, string otp);
		public event OnControlDisconnectRequestHandler OnControlDisconnectRequest = null;
		public delegate void OnControlDisconnectRequestHandler(string displayCode, string allowId);
		public event OnControlPauseVideoHandler OnControlPauseVideo = null;
		public delegate void OnControlPauseVideoHandler(string displayCode, string allowId);
		public event OnControlResumeVideoHandler OnControlResumeVideo = null;
		public delegate void OnControlResumeVideoHandler(string displayCode, string allowId);
		public event OnControlToggleFullscreenHandler OnControlToggleFullscreen = null;
		public delegate void OnControlToggleFullscreenHandler(string displayCode, string allowId);
		public event OnUpdateInstanceBindedIdHandler OnUpdateInstanceBindedId = null;
		public delegate void OnUpdateInstanceBindedIdHandler(string instanceId);
		public event OnControlGetStatReportHandler OnControlGetStatReport = null;
		public delegate void OnControlGetStatReportHandler(string displayCode, string allowId);

		// InstanceBindingSignaling SocketIO callback (Issuer: "MVBA or MVBW" Receiver: "Display")
		public event OnInstanceBindingConnectedHandler OnInstanceBindingConnected = null;
		public delegate void OnInstanceBindingConnectedHandler();
		public event OnInstanceBindingPlayRequestHandler OnInstanceBindingPlayRequest = null;
		public delegate void OnInstanceBindingPlayRequestHandler(string messageFor, string token, string action);
		public event OnInstanceBindingSetClientRequestHandler OnInstanceBindingSetClientRequest = null;
		public delegate void OnInstanceBindingSetClientRequestHandler(string messageFor, string token, string action, Dictionary<string, object> extra, string nextId);
		public event OnInstanceBindingStopRequestHandler OnInstanceBindingStopRequest = null;
		public delegate void OnInstanceBindingStopRequestHandler(string token, string action);

		// Error callback
		public event OnErrorHandler OnError = null;
		public delegate void OnErrorHandler(string failedReason);

		// NetworkConnectionChanged
		public event OnNetworkConnectionChangedHanlder OnNetworkConnectionChanged = null;
		public delegate void OnNetworkConnectionChangedHanlder(bool connected);

		public DisplayAPI(string deviceId)
		{
			m_DeviceId = deviceId;

			if (DisplayConfig.Instance.Environment == DisplayConfig.DeployEnvironment.Stage)
			{
				CodeMappingEndpoint = CodeMappingEndpoint_STAGE;
				InstanceBindingEndpoint = InstanceBindingEndpoint_STAGE;
				ControlSignalEndpoint = ControlSignalEndpoint_STAGE;
			}
			else
			{
				CodeMappingEndpoint = CodeMappingEndpoint_PRODUCTION;
				InstanceBindingEndpoint = InstanceBindingEndpoint_PRODUCTION;
				ControlSignalEndpoint = ControlSignalEndpoint_PRODUCTION;
			}
		}
		
		public async Task EstablishInstanceBindingSignaling(string instanceId)
		{
			await DisestablishInstanceBindingSignaling();

			var options = new SocketIOOptions();
			options.EnabledSslProtocols = System.Security.Authentication.SslProtocols.Tls12;
			options.Query = new Dictionary<string, string>();
			options.Query["clientType"] = "csharp";
			options.Query["socketCustomEvent"] = instanceId;

			// instance binding signaling
			m_InstanceBindingSignaling = new SocketIO(ControlSignalEndpoint, options);
			m_InstanceBindingSignaling.OnConnected += InstanceBindingSignaling_OnConnected;
			m_InstanceBindingSignaling.On(instanceId, new Action<SocketIOResponse>((response) =>
			{
				HandleInstanceBindingResponse(response.ToString());
			}));
			await m_InstanceBindingSignaling.ConnectAsync();
		}

		private void InstanceBindingSignaling_OnConnected(object sender, EventArgs e)
		{
			OnInstanceBindingConnected?.Invoke();
		}

		public async Task EstablishControlSignaling(string displayCode)
		{
			var options = new SocketIOOptions();
			options.EnabledSslProtocols = System.Security.Authentication.SslProtocols.Tls12;
			options.Query = new Dictionary<string, string>();
			options.Query["clientType"] = "csharp";
			options.Query["socketCustomEvent"] = displayCode;

			// control signaling
			m_ControlSignaling = new SocketIO(ControlSignalEndpoint, options);
			m_ControlSignaling.On(displayCode, new Action<SocketIOResponse>((response) =>
			{
				HandleControlSignalingResponse(response.ToString());
			}));
			m_ControlSignaling.OnConnected += ControlSignaling_OnConnected;
			m_ControlSignaling.OnDisconnected += ControlSignaling_OnDisconnected;
			await m_ControlSignaling.ConnectAsync();
		}

		public bool IsControlSignalingConnected()
		{
			if (m_ControlSignaling == null)
				return false;
			return m_ControlSignaling.Connected;
		}

		private void ControlSignaling_OnConnected(object sender, EventArgs e)
		{
			OnNetworkConnectionChanged?.Invoke(true);
		}

		private void ControlSignaling_OnDisconnected(object sender, string e)
		{
			OnNetworkConnectionChanged?.Invoke(false);
		}

		public async Task DisestablishInstanceBindingSignaling()
		{
			if (m_InstanceBindingSignaling != null && m_InstanceBindingSignaling.Connected)
				await m_InstanceBindingSignaling.DisconnectAsync();
		}

		private void HandleControlSignalingResponse(string response)
		{
			try
			{
				var responseJson = JsonConvert.DeserializeObject<dynamic>(response);
				if (responseJson is JArray array && array.Count > 0)
				{
					var req = array[0] as dynamic;
					if (req.messageFor != null && req.userid != null && req.otp != null) // MUST have "messageFor" field
					{
						// "receive connect request"
						// --> data: [{"messageeFor": $code, "userid": $allowId, "otp": $otp}]
						OnControlConnectRequest?.Invoke((string)req.messageFor, (string)req.userid, (string)req.otp);
					}
					else if (req.messageFor != null && req.userid != null && req.action != null)
					{
						string action = req.action;
						if (action == "pauseVideo")
							OnControlPauseVideo?.Invoke((string)req.messageFor, (string)req.userid);
						else if (action == "resumeVideo")
							OnControlResumeVideo?.Invoke((string)req.messageFor, (string)req.userid);
						else if (action == "disconnect")
							OnControlDisconnectRequest?.Invoke((string)req.messageFor, (string)req.userid);
						else if (action == "togglefullscreen")
							OnControlToggleFullscreen?.Invoke((string)req.messageFor, (string)req.userid);
						else if (action == "getstatreport")
							OnControlGetStatReport?.Invoke((string)req.messageFor, (string)req.userid);
					}
				}
				return;
			}
			catch (Exception)
			{
			}
			try
			{
				// e.g. ["XXXXXX"]
				var arrayData = JsonConvert.DeserializeObject<dynamic>(response);
				string instance = arrayData[0].Value as string;
				OnUpdateInstanceBindedId?.Invoke(instance);
			}
			catch (Exception)
			{
			}
		}

		private void HandleInstanceBindingResponse(string response)
		{
			try
			{
				//Trace.WriteLine("[Streamer] HandleInstanceBindingResponse: " + response);
				var responseJson = JsonConvert.DeserializeObject<dynamic>(response);
				if (responseJson is JArray array && array.Count > 0)
				{
					var req = array[0] as dynamic;
					var action = req.status.action.Value as string;
					var token = req.status.userid.Value as string;
					var messageFor = req.messageFor.Value as string;
					if (action == "play")
					{
						OnInstanceBindingPlayRequest?.Invoke(messageFor, token, action);
					}
					else if (action == "setClient")
					{
						var nextId = req.nextId.Value as string;
						Dictionary<string, object> extra = new Dictionary<string, object>();
						extra.Add("setClientId", req.extra.setClientId);
						extra.Add("setAllowedPeer", req.extra.setAllowedPeer);
						OnInstanceBindingSetClientRequest?.Invoke(messageFor, token, action, extra, nextId);
					}
				}
			}
			catch (Exception)
			{
			}
		}

		public async Task SendInstanceBindingSetClientReply(string instanceId, string action, string status, Dictionary<string, object> extra, string messageId, string nextId)
		{
			// { "messageFor": $allowed, "action": "control", "status": {action:"setClient", status: "ready"},
			//   extra: {setClientId, setAllowedPeer}, direction: "out", messageId: "$messageId" }
			InstanceBindingSetClientReply reply;
			reply.messageFor = instanceId;
			reply.action = "control";
			reply.status = new Dictionary<string, object>();
			reply.status.Add("action", action);
			reply.status.Add("status", status);
			reply.extra = extra;
			reply.direction = "out";
			reply.messageId = messageId;
			reply.nextId = nextId;
			var str = JsonConvert.SerializeObject(reply);
			await m_InstanceBindingSignaling.EmitAsync(instanceId, reply);
		}

		public async Task SendControlConnectReply(string displayCode, string allowId, string action, string streamerVersion)
		{
			// { "messageFor": $allowed, "action": 'connect', "display": $code,  "streamer": $streamer, "capacities": [$capacity]}
			ControlConnectReply reply;
			reply.display = displayCode;
			reply.action = action;
			reply.messageFor = allowId;
			reply.streamer = streamerVersion;
			reply.capacities = new List<string>();
			reply.capacities.Add("togglefullscreen");
			await m_ControlSignaling.EmitAsync(displayCode, reply);
		}

		public async Task SendControlStatReportReply(string displayCode, string allowId, string action, string data)
		{
			// { "messageFor": $allowed, "display": $code,  "streamer": $streamer, "capacities": [$capacity]}
			GetStatReportReply reply;
			reply.display = displayCode;
			reply.action = "getstatreport";
			reply.messageFor = allowId;
			reply.statreport = data;
			reply.capacities = new List<string>();
			reply.capacities.Add("getstatreport");
			await m_ControlSignaling.EmitAsync(displayCode, reply);
		}

		public async Task SendInstanceBindingOnUnpublishReply(string instanceId, string displayCode)
		{
			if (m_InstanceBindingSignaling == null)
				return;
			InstanceBindingOnUnpublishReply reply;
			reply.messageFor = instanceId;
			reply.display = displayCode;
			reply.action = "unPublish";
			await m_InstanceBindingSignaling.EmitAsync(instanceId, reply);
		}

		public async Task SendInstanceBindingOnConnectedReply(string instanceId, string displayCode, string streamerVersion)
		{
			if (m_InstanceBindingSignaling == null)
				return;
			InstanceBindingOnConnectReply reply;
			reply.messageFor = instanceId;
			reply.action = "join";
			reply.status = "open";
			reply.guestId = string.Format("Display_{0}({1})", displayCode, GenerateRandom(8));
			reply.direction = "out";
			reply.login = false;
			reply.extra = new Dictionary<string, object>();
			reply.extra.Add("streamer", streamerVersion);
			reply.extra.Add("code", displayCode);
			List<string> capacities = new List<string>();
			capacities.Add("togglefullscreen");
			reply.extra.Add("capacities", capacities);
			reply.extra.Add("platform", "windows");

			await m_InstanceBindingSignaling.EmitAsync(instanceId, reply);
		}

		public bool RegisterDisplayCode()
		{
			string url = string.Format("{0}/{1}", CodeMappingEndpoint, RegisterDisplayCode_PATH);
			string json = JsonConvert.SerializeObject(new RegisterDisplayCodeRequest()
			{
				deviceId = m_DeviceId,
				property = new Dictionary<string, string>()
			});
			var result = RestfulAPI(url, "POST", json);
			if (result == null)
			{
				OnNetworkConnectionChanged?.Invoke(false);
				return false;
			}
			else if (!result.Value.ok)
			{
				string failedReason = string.Format("RegisterDisplayCode HttpStatusCode[{0}] Response[{1}]",
					result.Value.statusCode, result.Value.webResponse);
				OnError?.Invoke(failedReason);
				return false;
			}
			else
			{
				try
				{
					var reply = JsonConvert.DeserializeObject<RegisterDisplayCodeReply>(result.Value.webResponse);
					OnRegisterDisplayCode?.Invoke(reply.code);
				}
				catch (Exception)
				{
					return false;
				}
			}
			return true;
		}

		public bool GetDisplayCodeByDeviceId(bool supressError)
		{
			string url = string.Format("{0}/{1}/{2}", CodeMappingEndpoint, GetDisplayCodeByDeviceId_PATH, m_DeviceId);
			var result = RestfulAPI(url, "GET");
			if (result == null)
			{
				OnNetworkConnectionChanged?.Invoke(false);
				return false;
			}
			else if (!result.Value.ok && !supressError)
			{
				string failedReason = string.Format("GetDisplayCodeByDeviceId HttpStatusCode[{0}] Response[{1}]",
					result.Value.statusCode, result.Value.webResponse);
				OnError?.Invoke(failedReason);
				return false;
			}
			else
			{
				try
				{
					var reply = JsonConvert.DeserializeObject<GetDisplayCodeByDeviceIdReply>(result.Value.webResponse);
					OnGetDisplayCode?.Invoke(reply.code);
				}
				catch (Exception)
				{
					return false;
				}
			}
			// should not reach here
			return true;
		}

		public bool GetOTP()
		{
			string url = string.Format("{0}/{1}/{2}", CodeMappingEndpoint, GetOTP_PATH, m_DeviceId);
			var result = RestfulAPI(url, "GET");
			if (result == null)
			{
				OnNetworkConnectionChanged?.Invoke(false);
				return false;
			}
			else if (!result.Value.ok)
			{
				string failedReason = string.Format("GetOTP HttpStatusCode[{0}] Response[{1}]",
					result.Value.statusCode, result.Value.webResponse);
				OnError?.Invoke(failedReason);
				return false;
			}
			else
			{
				try
				{
					string otp = result.Value.webResponse.Replace("\"", "");
					OnGetOTP?.Invoke(otp);
				}
				catch (Exception)
				{
					return false;
				}
			}
			return true;
		}

		public bool GetInstanceBinding(string displayCode, ref string instanceId)
		{
			string url = string.Format("{0}/{1}", InstanceBindingEndpoint, displayCode);
			var result = RestfulAPI(url, "GET");
			if (result == null)
			{
				OnNetworkConnectionChanged?.Invoke(false);
				return false;
			}
			else if (!result.Value.ok)
			{
				string failedReason = string.Format("GetInstanceBinding HttpStatusCode[{0}] Response[{1}]",
					result.Value.statusCode, result.Value.webResponse);
				OnError?.Invoke(failedReason);
				return false;
			}
			else
			{
				try
				{
					if (string.IsNullOrEmpty(result.Value.webResponse))
						return false;
					dynamic obj = JsonConvert.DeserializeObject(result.Value.webResponse);
					instanceId = obj.bind_to.Value as string;
				}
				catch (Exception)
				{
					return false;
				}
			}
			return true;
		}

		public IceServerQueryResult QueryIceServers()
		{
			var result = RestfulAPI(ICE_QUERY_URL, "GET");
			if (result == null)
			{
				OnNetworkConnectionChanged?.Invoke(false);
				return null;
			}
			else if (!result.Value.ok)
			{
				string failedReason = string.Format("QueryIceServers HttpStatusCode[{0}] Response[{1}]",
					result.Value.statusCode, result.Value.webResponse);
				OnError?.Invoke(failedReason);
				return null;
			}
			return JsonConvert.DeserializeObject<IceServerQueryResult>(result.Value.webResponse);
		}

		private string GenerateRandom(int length)
		{
			const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
			return new string(Enumerable.Repeat(chars, length).Select(s => s[m_Random.Next(s.Length)]).ToArray());
		}

		private RestfulAPIResult? RestfulAPI(string url, string method, string content = "")
		{
			HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
			request.Timeout = 10000;  // 10 seconds
			request.Method = method;

			byte[] byteArray = Encoding.UTF8.GetBytes(content);
			request.ContentLength = byteArray.Length;
			Stream newStream = null;
			StreamReader responseReader = null;
			HttpWebResponse webResponse = null;

			if (url.StartsWith("https", StringComparison.OrdinalIgnoreCase))
			{
				ServicePointManager.ServerCertificateValidationCallback = new RemoteCertificateValidationCallback(CheckValidationResult);
				ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls;
			}

			try
			{
				if (method.Equals("POST"))
				{
					request.ContentType = "application/json";
					newStream = request.GetRequestStream(); //open connection
					newStream.Write(byteArray, 0, byteArray.Length); // Send the data.
				}
				webResponse = (HttpWebResponse)request.GetResponse();
				Stream webStream = webResponse.GetResponseStream();
				responseReader = new StreamReader(webStream);
				RestfulAPIResult result = new RestfulAPIResult();
				result.statusCode = (int)webResponse.StatusCode;
				result.webResponse = responseReader.ReadToEnd();
				result.ok = (result.statusCode < 400);
				return result;
			}
			catch (WebException e)
			{
				webResponse = (HttpWebResponse)e.Response;
				if (webResponse != null)
				{
					RestfulAPIResult result = new RestfulAPIResult();
					result.statusCode = (int)webResponse.StatusCode;
					if ((int)webResponse.StatusCode == 403)
					{
						try
						{
							var webStream = webResponse.GetResponseStream();
							responseReader = new StreamReader(webStream);
							dynamic obj = JsonConvert.DeserializeObject(responseReader.ReadToEnd());
							if (obj != null && obj.responseCode != null)
								result.statusCode = obj.responseCode;
						}
						catch (Exception)
						{
							result.statusCode = 403;
						}
					}
					result.webResponse = result.statusCode.ToString();
					result.ok = false;
					return result;
				}
				return null;
			}
			finally
			{
				newStream?.Dispose();
				responseReader?.Dispose();
				webResponse?.Dispose();
			}
		}

		private bool CheckValidationResult(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors errors)
		{
			return true;// Always accept
		}
	}
}
