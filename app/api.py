from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
import sys
import os

# Ensure we can import remotetools if running from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from remotetools import RemoteAdmin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(title="Windows Remote Admin API", description="API wrapper for RemoteAdmin tools using Impacket")

class ConnectionInfo(BaseModel):
    machine: str = Field(..., description="Target machine IP or hostname")
    user: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    domain: str = Field(default="", description="Domain name (optional)")

class ShutdownRequest(ConnectionInfo):
    force: bool = Field(default=True, description="Force shutdown")
    reboot: bool = Field(default=False, description="Reboot instead of shutdown")

class ExecRequest(ConnectionInfo):
    command: str = Field(..., description="PowerShell command to execute")

class VolumeRequest(ConnectionInfo):
    level: int = Field(..., ge=0, le=100, description="Volume level (0-100)")

@app.post("/shutdown", summary="Shutdown or reboot remote machine")
async def shutdown(request: ShutdownRequest):
    """
    Triggers a shutdown or reboot on the remote machine using WMI and PowerShell.
    """
    try:
        admin = RemoteAdmin(
            machine=request.machine,
            user=request.user,
            password=request.password,
            domain=request.domain,
            logger=logger
        )
        admin.wmi_shutdown(force=request.force, reboot=request.reboot)
        action = "reboot" if request.reboot else "shutdown"
        return {"status": "success", "message": f"{action} command sent to {request.machine}"}
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/exec", summary="Execute PowerShell command")
# async def execute_command(request: ExecRequest):
#     """
#     Executes a PowerShell command on the remote machine via WMI.
#     Note: This does not return the command output, only the process creation status.
#     """
#     try:
#         admin = RemoteAdmin(
#             machine=request.machine,
#             user=request.user,
#             password=request.password,
#             domain=request.domain,
#             logger=logger
#         )
#         admin.wmi_powershell_exec(request.command)
#         return {"status": "success", "message": f"Command execution initiated on {request.machine}"}
#     except Exception as e:
#         logger.error(f"Execution failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/volume", summary="Set system volume")
async def set_volume(request: VolumeRequest):
    """
    Sets the system volume on the remote machine.
    Requires AudioDeviceCmdlets module to be installable/available on the target.
    """
    try:
        admin = RemoteAdmin(
            machine=request.machine,
            user=request.user,
            password=request.password,
            domain=request.domain,
            logger=logger
        )
        admin.set_volume(request.level)
        return {"status": "success", "message": f"Volume set to {request.level}% on {request.machine}"}
    except Exception as e:
        logger.error(f"Volume set failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/health", summary="Health check")
# async def health():
#     return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)