using DisplayUI.Integrations;
using DisplayWrapper;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Threading;

namespace DisplayDesktopApp
{
	public class DisplayFlow : IDisplayHostCallback
	{
		public string DeviceId { get; set; } = "";
		public string OTP { get; set; } = "";
		public string DisplayCode { get; set; } = "";
		public string InstanceId { get; set; } = "";
		public string CurrentAllowId { get; set; } = "";
		public string StreamerVersion { get; set; } = "";

		private object m_SyncObj = new object();
		private int m_RefreshOTPInterval = 30000; // default in ms
		private int m_RefreshOTPCountDown = 30000;  // in ms
		private DispatcherTimer m_Timer = null;
		private DisplayAPI m_DisplayAPI = null;
		private Random m_Random = new Random();
		private volatile bool m_Fullscreen = false;
		private volatile uint m_WaitForConnectStartTS = 0;
		private volatile bool m_IsStreaming = false;
		private volatile bool m_FromInstance = false;

		private IntPtr m_hwnd = IntPtr.Zero;
		private IDisplayHostServiceMgr m_HostSvcMgr = null;
		private IDisplayHostService m_HostSvc = null;
		private List<DisplayNative.IceServer> m_IceServers = new List<DisplayNative.IceServer>();

		// see "lock UI on stream" https://viewsonic-ssi.visualstudio.com/Display%20App/_wiki/wikis/Display-App.wiki/551/Display-API
		// We must remember last setClient info from instance.
		private string m_LastSetClientNextId = "";
		private Dictionary<string, object> m_LastSetClientExtra = new Dictionary<string, object>();

		private string m_VideoCodecs = "H264";
		private string m_AudioCodecs = "OPUS";
		private readonly string SignalingServer = GetEnvironmentVariable("SignalingServer", "https://mrtc.myviewboard.cloud");

		private string m_StatReport = "";

		public event OnOTPCountDownTickHandler OnOTPCountDownTick = null;
		public delegate void OnOTPCountDownTickHandler(int leftSeconds);

		public event OnUpdateOTPHandler OnUpdateOTP = null;
		public delegate void OnUpdateOTPHandler(string otp);

		public event OnDisplayCodeHandler OnDisplayCode = null;
		public delegate void OnDisplayCodeHandler(string displayCode, bool newRegistered);

		public event OnInstanceIdHandler OnInstanceId = null;
		public delegate void OnInstanceIdHandler(string instanceId);

		public event OnErrorHandler OnError = null;
		public delegate void OnErrorHandler(string failedReason);

		public event OnErrorResumeHandler OnErrorResume = null;
		public delegate void OnErrorResumeHandler();

		public event OnSetRemoteIdFinishedHandler OnSetRemoteIdFinished = null;
		public delegate void OnSetRemoteIdFinishedHandler();

		public event OnStreamAddedTimeoutHandler OnStreamAddedTimeout = null;
		public delegate void OnStreamAddedTimeoutHandler();

		public event OnStreamAddedHandler OnStreamAdded = null;
		public delegate void OnStreamAddedHandler(string streamId);

		public event OnStreamRemovedHandler OnStreamRemoved = null;
		public delegate void OnStreamRemovedHandler();

		public event OnRenderWindowClosedHandler OnRenderWindowClosed = null;
		public delegate void OnRenderWindowClosedHandler();

		public event OnNeedRestartHandler OnNeedRestart = null;
		public delegate void OnNeedRestartHandler();

		public event OnDisplayHostCrashHandler OnDisplayHostCrash = null;
		public delegate void OnDisplayHostCrashHandler();

		[DllImport("winmm")]
		static extern uint timeGetTime();

		public DisplayFlow(IDisplayHostServiceMgr hostSvcMgr)
		{
			m_HostSvcMgr = hostSvcMgr;
			m_HostSvcMgr.SetShowConsole(false);
			m_HostSvcMgr.SetDisplayHostExePath("DisplaySubprocess.exe");
		}

		~DisplayFlow()
		{
			StopHostService();
		}

		public static string GetEnvironmentVariable(string name, string defaultValue)
        {
			string value = Environment.GetEnvironmentVariable(name);
			return (value==null) ? defaultValue : value;
		}

		public bool Setup(string DeviceId, int RefreshOTPInterval = 30000 /*default in ms*/)
		{
			this.DeviceId = DeviceId;
			m_RefreshOTPCountDown = RefreshOTPInterval;
			m_RefreshOTPInterval = RefreshOTPInterval;

			m_DisplayAPI = new DisplayAPI(this.DeviceId);
			m_DisplayAPI.OnError += DisplayAPI_OnError;
			m_DisplayAPI.OnNetworkConnectionChanged += DisplayAPI_OnNetworkConnectionChanged;
			m_DisplayAPI.OnGetOTP += DisplayAPI_OnGetOTP;
			m_DisplayAPI.OnRegisterDisplayCode += DisplayAPI_OnRegisterDisplayCode;
			m_DisplayAPI.OnGetDisplayCode += DisplayAPI_OnGetDisplayCode;
			m_DisplayAPI.OnControlConnectRequest += DisplayAPI_OnControlConnectRequest;
			m_DisplayAPI.OnControlPauseVideo += DisplayAPI_OnControlPauseVideo;
			m_DisplayAPI.OnControlResumeVideo += DisplayAPI_OnControlResumeVideo;
			m_DisplayAPI.OnControlDisconnectRequest += DisplayAPI_OnControlDisconnectRequest;
			m_DisplayAPI.OnControlToggleFullscreen += DisplayAPI_OnControlToggleFullscreen;
			m_DisplayAPI.OnUpdateInstanceBindedId += DisplayAPI_OnInstanceBinded;
			m_DisplayAPI.OnInstanceBindingConnected += DisplayAPI_OnInstanceBindingSignalConnected;
			m_DisplayAPI.OnInstanceBindingPlayRequest += DisplayAPI_OnInstanceBindingPlayRequest;
			m_DisplayAPI.OnInstanceBindingStopRequest += DisplayAPI_OnInstanceBindingStopRequest;
			m_DisplayAPI.OnInstanceBindingSetClientRequest += DisplayAPI_OnInstanceBindingSetClientRequest;
			m_DisplayAPI.OnControlGetStatReport += DisplayAPI_OnControlGetStatReport;

			m_Timer = new DispatcherTimer();
			m_Timer.Interval = new TimeSpan(0, 0, 0, 0, 100);
			m_Timer.Tick += Timer_Tick;

			return true;
		}

		private void DisplayAPI_OnNetworkConnectionChanged(bool connected)
		{
			if (!connected)
			{
				OnError?.Invoke(DisplayWPF.Utility.StringFromTable("ERROR_NO_INTERNET"));
				StopAndStartHostService();
			}
			else
			{
				ForceRefreshOTP();
				OnErrorResume?.Invoke();
			}
		}

		private void DisplayAPI_OnInstanceBindingSetClientRequest(string messageFor, string token, string action, Dictionary<string, object> extra, string nextId)
		{
			Log(string.Format("DisplayAPI_OnInstanceBindingSetClientRequest messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;

			// MVBW allows interrupts the connection.
			// see https://viewsonic-ssi.visualstudio.com/Display%20App/_workitems/edit/19870/
			ApplicationInsights.AddEvent("streamSwitched");
			bool isStreamingFromWebClient = (m_IsStreaming && !m_FromInstance);
			if (isStreamingFromWebClient)
			{
				StopAndStartHostService();
				PostAction(new Action(async () =>
				{
					await m_DisplayAPI.SendControlConnectReply(DisplayCode, CurrentAllowId, "unPublish", StreamerVersion);
					SetupRemoteId(token, InstanceId, true);

					// Remember extra and nextId 
					m_LastSetClientNextId = GenerateNextId();
					m_LastSetClientExtra = extra;

					await m_DisplayAPI.SendInstanceBindingSetClientReply(InstanceId, "setClient", "ready", extra, nextId, m_LastSetClientNextId);
					OnSetRemoteIdFinished?.Invoke();
				}));
			}
			else
			{
				SetupRemoteId(token, InstanceId, true);
				PostAction(new Action(async () =>
				{
					// Remember extra and nextId 
					m_LastSetClientNextId = GenerateNextId();
					m_LastSetClientExtra = extra;

					await m_DisplayAPI.SendInstanceBindingSetClientReply(InstanceId, "setClient", "ready", extra, nextId, m_LastSetClientNextId);
					OnSetRemoteIdFinished?.Invoke();
				}));
			}
		}

		private void DisplayAPI_OnInstanceBindingStopRequest(string token, string action)
		{
			HandleStreamRemove();
			StopAndStartHostService();
		}

		private void DisplayAPI_OnInstanceBindingPlayRequest(string messageFor, string token, string action)
		{
			Log(string.Format("DisplayAPI_OnInstanceBindingPlayRequest messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;
		}

		private async void DisplayAPI_OnInstanceBindingSignalConnected()
		{
			await m_DisplayAPI.SendInstanceBindingOnConnectedReply(InstanceId, DisplayCode, StreamerVersion);
		}

		private async void DisplayAPI_OnInstanceBinded(string instanceId)
		{
			if (InstanceId == instanceId)
			{
				// do nothing
				return;
			}

			bool forceDisconnect = (InstanceId != "" && instanceId == "");

			InstanceId = instanceId;
			if (InstanceId != "")
				await m_DisplayAPI.EstablishInstanceBindingSignaling(InstanceId);

			OnInstanceId?.Invoke(InstanceId);

			if (forceDisconnect)
			{
				// close render window
				PostAction(new Action(() =>
				{
					m_HostSvc.NotifyRemoteUnpublishStream();
					HandleStreamRemove();
				}));

				// unPublish and disconnect
				PostAction(new Action(async () =>
				{
					await m_DisplayAPI.SendControlConnectReply(DisplayCode, CurrentAllowId, "unPublish", StreamerVersion);
					await m_DisplayAPI.DisestablishInstanceBindingSignaling();
				}));

				// WORKAROUND
				// If we disconnect and reconnect to owt signaling server, we can't get the stream anymore.
				// Currently, we just restart display app to avoid this issue..
				PostAction(new Action(() =>
				{
					OnNeedRestart?.Invoke();
				}));
			}
		}

		private void DisplayAPI_OnControlPauseVideo(string messageFor, string allowId)
		{
			Log(string.Format("DisplayAPI_OnControlPauseVideo messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;

			m_HostSvc.EnableAudio(false);
			ApplicationInsights.AddEvent("streamPaused");
		}

		private void DisplayAPI_OnControlResumeVideo(string messageFor, string allowId)
		{
			Log(string.Format("DisplayAPI_OnControlResumeVideo messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;

			m_HostSvc.EnableAudio(true);
			ApplicationInsights.AddEvent("streamResumed");
		}

		private void DisplayAPI_OnControlDisconnectRequest(string messageFor, string allowId)
		{
			Log(string.Format("DisplayAPI_OnControlDisconnectRequest messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;

			if (CurrentAllowId == allowId)
			{
				// DAMN.. Intel OWT crash if we remove allow id..
				//m_HostSvc.RemoveAllowedRemoteId(allowId);
				HandleStreamRemove();
				StopAndStartHostService();
			}
		}

		private void DisplayAPI_OnControlToggleFullscreen(string messageFor, string allowId)
		{
			Log(string.Format("DisplayAPI_OnControlToggleFullscreen messageFor[{0}]", messageFor));
			if (!IsMessageForMe(messageFor))
				return;

			m_HostSvc.ToggleFullscreen();
			ApplicationInsights.AddEvent("fullscreenToggled");
		}

		private async void DisplayAPI_OnControlConnectRequest(string messageFor, string allowId, string otp)
		{
			Log(string.Format("DisplayAPI_OnControlConnectRequest messageFor[{0}]", messageFor));

			string action = "";
			bool setupRemoteIdSuccess = false;
			if (messageFor != DisplayCode || otp != OTP)
			{
				action = "denied";
			}
			else
			{
				setupRemoteIdSuccess = SetupRemoteId(DisplayCode, allowId, false);
				if (setupRemoteIdSuccess)
					action = "connect";
				else
					action = "blocked";
			}
			Log(string.Format("OnControlConnectRequest displayCode:{0} allowId:{1} otp:{2} reply:{3}", messageFor, allowId, otp, action));
			await m_DisplayAPI.SendControlConnectReply(messageFor, allowId, action, StreamerVersion);
			if (setupRemoteIdSuccess)
				OnSetRemoteIdFinished?.Invoke();
		}

		private async void DisplayAPI_OnControlGetStatReport(string messageFor, string allowId)
		{
			Log(string.Format("DisplayAPI_OnControlGetStatReport messageFor[{0}]", messageFor));

			if (!IsMessageForMe(messageFor))
				return;

			string action = "getstatreport";
			await m_DisplayAPI.SendControlStatReportReply(messageFor, allowId, action, m_StatReport);
		}

		private bool SetupRemoteId(string token, string remoteId, bool fromInstance)
		{
			if (token == "" || remoteId == "")
				return false;

			lock (m_SyncObj)
			{
				m_FromInstance = fromInstance;

				if ((fromInstance == false) && (CurrentAllowId != ""))
					return false;

				CurrentAllowId = remoteId;
				m_WaitForConnectStartTS = timeGetTime();

				m_HostSvc.ConnectToSingalingServer(SignalingServer, token);
				m_HostSvc.AddAllowedRemoteId(remoteId);
				m_HostSvc.SetDefaultFullscreenMode(m_Fullscreen);
			}
			return true;
		}

		private bool IsMessageForMe(string messageFor)
		{
			if (string.IsNullOrEmpty(messageFor))
				return false;

			if (string.IsNullOrEmpty(DisplayCode))
				return false;

			if (DisplayCode != messageFor)
				return false;

			return true;
		}

		private void HandleStreamAdd(string streamId)
		{
			lock (m_SyncObj)
			{
				m_IsStreaming = true;
				m_WaitForConnectStartTS = 0;
			}
			PostAction(new Action(async () =>
			{
				// send only once
				if (InstanceId != "" && m_LastSetClientNextId != "" && m_LastSetClientExtra.Count > 0)
				{
					await m_DisplayAPI.SendInstanceBindingSetClientReply(InstanceId, "play", "streamAdded", m_LastSetClientExtra, m_LastSetClientNextId, GenerateNextId());
					m_LastSetClientNextId = "";
					m_LastSetClientExtra.Clear();
				}
			}));
			OnStreamAdded?.Invoke(streamId);
		}

		private void HandleStreamRemove()
		{
			lock (m_SyncObj)
			{
				CurrentAllowId = "";
				m_IsStreaming = false;
				m_WaitForConnectStartTS = 0;
			}
			OnStreamRemoved?.Invoke();
		}

		private void HandleVideoRendererClose()
		{
			lock (m_SyncObj)
			{
				CurrentAllowId = "";
				m_IsStreaming = false;
				m_WaitForConnectStartTS = 0;
			}
			PostAction(new Action(async () =>
			{
				try
				{
					await m_DisplayAPI.SendControlConnectReply(DisplayCode, CurrentAllowId, "unPublish", StreamerVersion);
					if (InstanceId != "")
						await m_DisplayAPI.SendInstanceBindingOnUnpublishReply(InstanceId, DisplayCode);
				}
				catch (Exception)
				{
				}
			}));
			ForceRefreshOTP();
			OnRenderWindowClosed?.Invoke();
		}

		private void HandleGetStatReport(string data)
		{
			m_StatReport = data;
		}

		private void DisplayAPI_OnGetOTP(string otp)
		{
			otp = "0000";
			OTP = otp;
			if (m_DisplayAPI != null && m_DisplayAPI.IsControlSignalingConnected())
				OnErrorResume?.Invoke();
			OnUpdateOTP?.Invoke(otp);
		}

		private void DisplayAPI_OnRegisterDisplayCode(string displayCode)
		{
			DisplayCode = displayCode;
			OnDisplayCode?.Invoke(displayCode, true);
		}

		private void DisplayAPI_OnGetDisplayCode(string displayCode)
		{
			DisplayCode = displayCode;
			OnDisplayCode?.Invoke(displayCode, false);
		}

		private void DisplayAPI_OnError(string failedReason)
		{
			OnError?.Invoke(failedReason);
		}

		public void StartOTPCountdownTimer()
		{
			m_Timer?.Start();
		}

		public bool IsControlSignalingConnected()
		{
			if (m_DisplayAPI != null)
				return m_DisplayAPI.IsControlSignalingConnected();
			return false;
		}

#pragma warning disable 1998
		public async void Start(IntPtr hwnd, Action onReady)
		{
			m_hwnd = hwnd;

			Func<Task<bool>> get_display_code = async () =>
			{
				if (!GetDisplayCode())
				{
					Log("Start::GetDisplayCode() failed");
					return false;
				}
				Log("Start::GetDisplayCode() succeed");
				return true;
			};
			Func<Task<bool>> refresh_otp = async () =>
			{
				if (!RefreshOTP())
				{
					Log("Start::RefreshOTP() failed");
					return false;
				}
				Log("Start::RefreshOTP() succeeded");
				return true;
			};
			Func<Task<bool>> get_instance_binding = async () =>
			{
				string instanceId = "";
				if (m_DisplayAPI.GetInstanceBinding(DisplayCode, ref instanceId))
				{
					Log("Start::GetInstanceBinding() succeeded");
					InstanceId = instanceId;
					OnInstanceId?.Invoke(InstanceId);
				}
				else
				{
					Log("Start::GetInstanceBinding() skip");
				}
				return true;
			};
			Func<Task<bool>> query_ice_servers = async () =>
			{
				var query_ice_servers1 = m_DisplayAPI.QueryIceServers();
				if (query_ice_servers1 != null && query_ice_servers1.list != null)
				{
					foreach (var query_ice_server in query_ice_servers1.list)
					{
						m_IceServers.Add(new DisplayNative.IceServer()
						{
							url = query_ice_server.url,
							account = query_ice_server.username,
							password = query_ice_server.credential,
						});
					}

					Log("Start::QueryIceServers() success");
					return true;
				}
				else
				{
					Log("Start::QueryIceServers() failed");
				}
				return false;
			};
			Func<Task<bool>> establish_control_signaling = async () =>
			{
				await m_DisplayAPI.EstablishControlSignaling(DisplayCode);
				Log("Start::EstablishControlSignaling()");
				return true;
			};
			Func<Task<bool>> establish_instance_bindingsignaling = async () =>
			{
				if (InstanceId != "")
				{
					await m_DisplayAPI.EstablishInstanceBindingSignaling(InstanceId);
					Log("Start::EstablishInstanceBindingSignaling()");
				}
				else
				{
					Log("Start::EstablishInstanceBindingSignaling() skip");
				}
				return true;
			};
			Func<Task<bool>> start_host_service = async () =>
			{
				StartHostService();
				Log("Start::StartHostService()");
				onReady?.Invoke();
				return true;
			};
			var actions = new List<Func<Task<bool>>>()
			{
				get_display_code,
				refresh_otp,
				get_instance_binding,
				query_ice_servers,
				establish_control_signaling,
				establish_instance_bindingsignaling,
				start_host_service
			};
			PostActions(actions);
		}
#pragma warning restore 1998

		private void StopAndStartHostService()
		{
			StopHostService();
			StartHostService();
		}

		private void StartHostService()
		{
			if (m_HostSvc == null)
			{
				m_HostSvc = m_HostSvcMgr.StartDisplayHostService(this);
				var config = new DisplayNative.ConfigureParameter();
				// TODO report connection stats
				config.report_conn_stats = 1;
				m_HostSvc.Configure(config);
				m_HostSvc.Initialize(m_VideoCodecs, m_AudioCodecs, m_IceServers.Count, m_IceServers.ToArray());
				var webrtcLogPath = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
					"Display");
				if (System.IO.Directory.Exists(webrtcLogPath))
				{
					const int fileSize = 50 * 1024 * 1024;
					m_HostSvc.SetWebrtcLoggingConfig((int)DisplayNative.WEBRTC_LOGGING_SERVERITY_VERBOSE, webrtcLogPath, fileSize);
				}
				m_HostSvc.SetupVideoRenderer("myViewboard Display", m_hwnd, DisplayNative.VIDEO_PRESENTER_TYPE_D3D11);
			}
		}

		private void StopHostService(bool shutdown = true)
		{
			if (m_HostSvc != null)
			{
				m_HostSvcMgr.CloseDisplayHostService(m_HostSvc, shutdown);
				m_HostSvc = null;
			}
		}

		private void PostAction(Action action)
		{
			ThreadPool.QueueUserWorkItem(new WaitCallback(o =>
			{
				action?.Invoke();
			}));
		}

		private void PostActions(IList<Func<Task<bool>>> actions, int asyncWaitMS = 1000)
		{
			ThreadPool.QueueUserWorkItem(new WaitCallback(async (o) =>
			{
				int i = 0;
				int actionSize = actions.Count;
				bool hasError = false;
				do
				{
					do
					{
						var action = actions[i];
						if (await action())
							break; // contine next action..
						hasError = true;
						await Task.Delay(asyncWaitMS);
					} while (true);
					i++;
				} while (i < actionSize);

				// done.. 
				if (hasError)
					OnErrorResume?.Invoke();
			}));
		}

		private void Log(string msg)
		{
			Trace.WriteLine(string.Format("[Display] {0}", msg));
		}

		public void Stop()
		{
			if (m_Timer != null)
				m_Timer.Stop();

			m_Timer = null;
			DeviceId = "";
			OTP = "";
			DisplayCode = "";
		}

		public string GetOTP()
		{
			return OTP;
		}

		public void ForceRefreshOTP()
		{
			m_RefreshOTPCountDown = m_RefreshOTPInterval;
			OnOTPCountDownTick?.Invoke(m_RefreshOTPCountDown);
			PostAction(new Action(() => { RefreshOTP(); }));
		}

		public void SetFullscreenMode(bool fullscreen)
		{
			m_Fullscreen = fullscreen;
		}

		private void Timer_Tick(object sender, EventArgs e)
		{
			CheckStreamStatus();
			HandleOTPCountDown();
		}

		private void CheckStreamStatus()
		{
			bool timeout = false;
			lock (m_SyncObj)
			{
				if ((CurrentAllowId == "") || (m_WaitForConnectStartTS == 0) || m_FromInstance)
					return;
				const int timeoutMS = 30 * 1000; // 30 seconds 
				var elapsedMS = timeGetTime() - m_WaitForConnectStartTS;
				if ((elapsedMS >= timeoutMS) && !m_IsStreaming)
				{
					timeout = true;
					CurrentAllowId = "";
					m_IsStreaming = false;
					m_WaitForConnectStartTS = 0;
				}
			}
			if (timeout)
			{
				PostAction(new Action(async () =>
				{
					try
					{
						Log("HandleConnectTimeout reply: timeout");
						await m_DisplayAPI.SendControlConnectReply(DisplayCode, CurrentAllowId, "timeout", StreamerVersion);
					}
					catch (Exception)
					{
					}
					OnStreamAddedTimeout?.Invoke();
				}));
			}
		}

		private void HandleOTPCountDown()
		{
			if (m_RefreshOTPCountDown <= 0)
			{
				RefreshOTP();
				m_RefreshOTPCountDown = m_RefreshOTPInterval;
			}
			else
				m_RefreshOTPCountDown -= 100;  // in ms

			OnOTPCountDownTick?.Invoke(m_RefreshOTPCountDown);
		}

		private bool GetDisplayCode()
		{
			if (m_DisplayAPI.GetDisplayCodeByDeviceId(true) || m_DisplayAPI.RegisterDisplayCode())
				return true;

			return false;
		}

		private bool RefreshOTP()
		{
			return m_DisplayAPI.GetOTP();
		}

		public string GenerateNextId()
		{
			// see https://hexdocs.pm/nanoid/Nanoid.html
			const int length = 21;
			const string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
			return new string(Enumerable.Repeat(chars, length).Select(s => s[m_Random.Next(s.Length)]).ToArray());
		}

		public void OnProcessExit(string name, int exitCode)
		{
			if (exitCode == 0)
				return;
			StopHostService(false);
			StartHostService();
			OnDisplayHostCrash?.Invoke();
		}

		public void OnDisplayStatus(string name, int type, string id, string data)
		{
			switch (type)
			{
				case DisplayNative.DISPLAY_STATUS_CALLBACK_TYPE_STREAMADDED:
					HandleStreamAdd(id);
					break;

				case DisplayNative.DISPLAY_STATUS_CALLBACK_TYPE_VIDEORENDERER_CLOSED:
					HandleVideoRendererClose();
					break;

				case DisplayNative.DISPLAY_STATUS_CALLBACK_TYPE_STREAMREMOVEED:
					HandleStreamRemove();
					break;

				case DisplayNative.DISPLAY_STATUS_CALLBACK_TYPE_GETSTATS:
					HandleGetStatReport(data);
					break;

				default:
					break;
			}
		}

		public void OnPublishStreamSuccess(string name, string id)
		{
			// do nothing..
		}

		public void OnPublishStreamError(string name, string id, string errorMessage)
		{
			// do nothing..
		}
	}
}
