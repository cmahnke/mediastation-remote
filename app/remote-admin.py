import argparse
import sys
from remotetools import RemoteAdmin
from impacket.examples import logger as impacket_logger

def main():
    parser = argparse.ArgumentParser(description="Impacket Unified Remote Admin")
    parser.add_argument("--machine", "-m", required=True, help="Target machine")
    parser.add_argument("--user", "-u", required=True, help="Username")
    parser.add_argument("--password", "-p", required=True, help="Password")
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

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    impacket_logger.init(args.ts, args.debug)

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