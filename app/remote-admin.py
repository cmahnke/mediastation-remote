import argparse
import sys
from remotetools import RemoteAdmin, WOL
from impacket.examples import logger as impacket_logger
import wakeonlan

def main():
    parser = argparse.ArgumentParser(description="Impacket Unified Remote Admin")
    parser.add_argument("--machine", "-m", help="Target machine")
    parser.add_argument("--user", "-u", help="Username")
    parser.add_argument("--password", "-p", help="Password")
    parser.add_argument("--domain", "-d",  default=".", help="Domain name")
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    parser.add_argument('-ts', action='store_true', help='Adds timestamp to every logging output')

    subparsers = parser.add_subparsers(dest='action', required=True)

    # Shutdown command
    shutdown_parser = subparsers.add_parser('shutdown', help='Shutdown the remote machine')
    shutdown_parser.add_argument("--timeout", type=int, default=0, help="Shutdown timeout in seconds")
    shutdown_parser.add_argument("--no-force", action='store_false', dest='force', help="Do not force applications to close")

    # Reboot command
    reboot_parser = subparsers.add_parser('reboot', help='Reboot the remote machine')
    reboot_parser.add_argument("--timeout", type=int, default=0, help="Reboot timeout in seconds")
    reboot_parser.add_argument("--no-force", action='store_false', dest='force', help="Do not force applications to close")

    # Exec command
    exec_parser = subparsers.add_parser('exec', help='Execute a PowerShell command')
    exec_parser.add_argument("--command", required=True, help="PowerShell command to execute")

    # Volume command
    volume_parser = subparsers.add_parser('volume', help='Set system volume')
    volume_parser.add_argument("--level", type=int, choices=range(0, 101), required=True, help="Volume level (0-100)")

    # WOL command
    wol_parser = subparsers.add_parser('wol', help='Wake on LAN')
    wol_parser.add_argument("mac", help="MAC address")
    wol_parser.add_argument("--broadcast", default=wakeonlan.BROADCAST_IP, help="Broadcast IP")
    wol_parser.add_argument("--port", type=int, default=wakeonlan.DEFAULT_PORT, help="Port")
    wol_parser.add_argument("--interface", help="Interface IP")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    impacket_logger.init(args.ts, args.debug)

    if args.action == 'wol':
        wol = WOL(args.mac, args.interface, args.broadcast, args.port)
        wol.send_magic_packet()
        return

    if not args.machine or not args.user or not args.password:
        parser.error("the following arguments are required: --machine/-m, --user/-u, --password/-p")

    admin = RemoteAdmin(args.machine, args.user, args.password, args.domain)

    if args.action == 'shutdown':
        admin.wmi_shutdown(force=args.force, reboot=False)
    elif args.action == 'reboot':
        admin.wmi_shutdown(force=args.force, reboot=True)
    elif args.action == 'exec':
        admin.wmi_powershell_exec(args.command)
    elif args.action == 'volume':
        admin.set_volume(args.level)

if __name__ == "__main__":
    main()