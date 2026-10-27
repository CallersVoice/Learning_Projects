import csv


def read_devices():
    with open("network_devices.csv", newline="", encoding="utf-8-sig") as file:
        devices = list(csv.DictReader(file))
    return devices


def main():
    devices = read_devices()

    print("Network devices:")
    for device in devices:
        print(device["Device Name"])

    print(f"\nTotal devices: {len(devices)}")


if __name__ == "__main__":
    main()
