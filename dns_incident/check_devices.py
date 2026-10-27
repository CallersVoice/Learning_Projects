import ipaddress
import subprocess

from list_devices import read_devices


# Use SSH keys or enter passwords when SSH asks.
SSH_PORT = 22


def ping_device(address):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", address],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "Responded"
        if result.returncode == 1:
            return "No reply (SSH will still be checked)"
        return "Ping error: " + result.stderr.strip()
    except FileNotFoundError:
        return "Ping command is not installed"
    except subprocess.TimeoutExpired:
        return "Ping timed out (SSH will still be checked)"


def check_dns(device, address):
    username = device["Username"].strip()
    if not username or username.lower() == "none":
        print("DNS: No SSH username available")
        return

    if device["OS"].strip() == "Ubuntu":
        command = "resolvectl status || cat /etc/resolv.conf"
    else:
        command = "cat /etc/resolv.conf"

    try:
        result = subprocess.run(
            ["ssh", "-p", str(SSH_PORT), "-o", "ConnectTimeout=5",
             "-o", "ConnectionAttempts=1", "-l", username, address, command],
            capture_output=True, text=True, timeout=90
        )
        if result.returncode != 0:
            print("DNS: SSH or DNS inspection failed")
            print(result.stderr.strip())
        elif result.stdout.strip():
            print("DNS configuration:")
            print(result.stdout.strip())
            print("Compare these settings with the approved lab configuration.")
        else:
            print("DNS: No configuration returned")
    except FileNotFoundError:
        print("DNS: SSH command is not installed")
    except subprocess.TimeoutExpired:
        print("DNS: SSH timed out")


def main():
    for device in read_devices():
        address = device["Device Address"].strip()
        print(f"\n{device['Device Name']} | {address}", flush=True)
        try:
            ipaddress.IPv4Address(address)
        except ipaddress.AddressValueError:
            print("Status: Discover a management IP through DHCP leases or the console.")
            continue

        print("Ping:", ping_device(address), flush=True)
        check_dns(device, address)

    print("\nChecks complete. DNS differences require investigation.")


if __name__ == "__main__":
    main()
