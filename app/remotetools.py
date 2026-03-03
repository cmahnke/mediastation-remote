import base64
import logging
from impacket.dcerpc.v5 import dcomrt
from impacket.dcerpc.v5.dcom import wmi
from impacket.smbconnection import  compute_lmhash, compute_nthash
from impacket.dcerpc.v5.dtypes import NULL
import wakeonlan

class RemoteAdmin:
    pwsh = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand'
    machine = '.'
    namespace = '\\\\%s\\root\\cimv2' % machine

    def __init__(self, machine, user, password, domain='', namespace=namespace, pwsh=pwsh, logger=None):
        self.target = machine
        self.user = user
        self.password = password
        self.domain = domain
        self.dcom = None
        self.lmhash = compute_lmhash(password)
        self.nthash = compute_nthash(password)
        self.pwsh = pwsh
        self.namespace = namespace
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    def wmi_connect(self):
        self.dcom = dcomrt.DCOMConnection(self.target, self.user, self.password, self.domain, self.lmhash, self.nthash)
        iInterface = self.dcom.CoCreateInstanceEx(wmi.CLSID_WbemLevel1Login, wmi.IID_IWbemLevel1Login)
        iWbemLevel1Login = wmi.IWbemLevel1Login(iInterface)
        iWbemServices = iWbemLevel1Login.NTLMLogin(self.namespace, NULL, NULL)
        iWbemLevel1Login.RemRelease()
        
        return iWbemServices

    def wmi_shutdown(self, force=True, reboot=False):
        cmd = "Stop-Computer"
        if force:
            cmd += " -Force"
        if reboot:
            cmd += " -Restart"
        self.logger.debug(f"Shutting down {self.target} using {cmd}...")
        self.wmi_powershell_exec(cmd)

    # TODO: Another way to use WMI fore shutdown directly https://github.com/fortra/impacket/blob/9d3d86ea30858cc74e6f080a7c2888811a7f40dd/examples/wmiexec.py#L286
    def wmi_powershell_exec(self, command):
        encoded_cmd = base64.b64encode(command.encode('utf-16le')).decode('ascii')
        full_command = f"{self.pwsh} {encoded_cmd}"

        try:
            iWbemServices = self.wmi_connect()
            iWbemClass, _ = iWbemServices.GetObject('Win32_Process')
            self.logger.info(f"Running {full_command} on {self.target}...")
            res = iWbemClass.Create(full_command, '\\', None)

            if res.ReturnValue == 0:
                self.logger.debug(f"WMI Process created. ProcessID: {res.ProcessId}")
            else:
                error_msg = f"WMI Create failed with code: {res.ReturnValue}"
                self.logger.warning(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"WMI Create error: {str(e)}")
            raise
        finally:
            if self.dcom:
                self.dcom.disconnect()

    def set_volume(self, level):
        ps_script = f"""
        if (-not (Get-Module -ListAvailable -Name AudioDeviceCmdlets)) {{
            try {{
                Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
                Install-Module -Name AudioDeviceCmdlets -Scope AllUsers -Force -AllowClobber -ErrorAction Stop
            }} catch {{
                Write-Error "Failed to install AudioDeviceCmdlets. Error: $_"
                exit 1
            }}
        }}
        try {{
            Set-AudioDevice -PlaybackVolume {level} -ErrorAction Stop
        }} catch {{
            Write-Error "Failed to set volume. Error: $_"
            exit 1
        }}
        """
        self.logger.debug(f"Attempting to set volume to {level}%% on {self.target}...")
        self.wmi_powershell_exec(ps_script)

class WOL:
    def __init__(self, machine, interface=None, broadcast=wakeonlan.BROADCAST_IP, port=wakeonlan.DEFAULT_PORT):
        self.machine = machine
        self.interface = interface
        self.broadcast = broadcast
        self.port = port

    def send_magic_packet(self):
        wakeonlan.send_magic_packet(self.machine, ip_address=self.broadcast, interface=self.interface, port=self.port)