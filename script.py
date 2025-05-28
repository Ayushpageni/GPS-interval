def convert_to_seconds(hhmmss):
    hours = int(hhmmss[0:2])
    minutes = int(hhmmss[2:4])
    seconds = int(hhmmss[4:6])
    return hours * 3600 + minutes * 60 + seconds

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def main():
    filename = input("Enter your GPS log file name: ")

    durations = []  # to store total time in V status
    time_ranges = []  # to store start and end time of each V period

    start_v = None
    last_v = None
    is_in_v_mode = False

    try:
        with open(filename, 'r') as file:
            for line in file:
                if not line.startswith('$GNRMC'):
                    continue

                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue

                status = parts[2]
                raw_time = parts[1]

                if len(raw_time) < 6:
                    continue

                current_time = convert_to_seconds(raw_time)

                if status == 'V':
                    if not is_in_v_mode:
                        start_v = current_time  # first time we see V
                        is_in_v_mode = True
                    last_v = current_time  # keep updating last time we see V

                elif status == 'A':
                    if is_in_v_mode and start_v is not None:
                        duration = last_v - start_v
                        if duration < 0:
                            duration += 24 * 3600  # handle if log rolls over midnight
                        durations.append(duration)
                        time_ranges.append((start_v, last_v))
                        start_v = None
                        last_v = None
                        is_in_v_mode = False

        # In case file ends while still in V mode
        if is_in_v_mode and start_v is not None and last_v is not None:
            duration = last_v - start_v
            if duration < 0:
                duration += 24 * 3600
            durations.append(duration)
            time_ranges.append((start_v, last_v))

        # Print results
        if durations:
            print("\n⏱️ Times when GPS had no fix (status 'V'):\n")
            for i in range(len(durations)):
                print(f"🟡 Period {i+1}:")
                print(f"    Start time : {format_time(time_ranges[i][0])}")
                print(f"    End time   : {format_time(time_ranges[i][1])}")
                print(f"    Duration   : {format_duration(durations[i])}\n")
        else:
            print("✅ No GPS 'V' (no fix) periods found in the file.")

    except FileNotFoundError:
        print(f"❌ File '{filename}' not found.")
    except Exception as e:
        print(f"⚠️ Something went wrong: {e}")

main()
