import pandas as pd
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

START_DATE = datetime(2026, 1, 1)
DAYS = 30

OFFICE_HOURS = range(9, 18)

EVENTS_WITH_IP = [4624, 4625, 4648, 4768, 4769]
EVENTS_NO_IP = [4672, 4688, 4634, 5058, 5061]

ALL_EVENTS = EVENTS_WITH_IP + EVENTS_NO_IP

PROCESS_LIST = [
    "explorer.exe",
    "chrome.exe",
    "powershell.exe",
    "cmd.exe",
    "svchost.exe",
    "services.exe",
    "winlogon.exe",
]

BURST_PROBABILITY = 0.08

# -----------------------------
# HOST GENERATION
# -----------------------------

WORKSTATIONS = [f"WS-{i:03}" for i in range(1, 51)]
SERVERS = [f"SRV-{i:02}" for i in range(1, 11)]
DOMAIN_CONTROLLERS = ["DC-01", "DC-02"]
ADMIN_HOSTS = [f"ADMIN-{i:02}" for i in range(1, 4)]

ALL_HOSTS = WORKSTATIONS + SERVERS + DOMAIN_CONTROLLERS + ADMIN_HOSTS

# -----------------------------
# USER GENERATION
# -----------------------------

def generate_users():

    users = []

    for i in range(30):
        users.append({
            "name": f"user{i}",
            "role": "employee",
            "shift": "day",
            "home_host": random.choice(WORKSTATIONS)
        })

    for i in range(10):
        users.append({
            "name": f"night_user{i}",
            "role": "employee",
            "shift": "night",
            "home_host": random.choice(WORKSTATIONS)
        })

    for i in range(5):
        users.append({
            "name": f"admin{i}",
            "role": "admin",
            "shift": "mixed",
            "home_host": random.choice(ADMIN_HOSTS)
        })

    for i in range(5):
        users.append({
            "name": f"tester{i}",
            "role": "tester",
            "shift": "mixed",
            "home_host": random.choice(WORKSTATIONS)
        })

    system_accounts = ["SYSTEM", "LOCAL_SERVICE", "NETWORK_SERVICE", "svc_backup", "svc_sql"]

    for s in system_accounts:
        users.append({
            "name": s,
            "role": "system",
            "shift": "system",
            "home_host": random.choice(SERVERS)
        })

    return users


# -----------------------------
# HOST SELECTION
# -----------------------------

def select_host(user):

    if user["role"] == "employee":
        return user["home_host"] if random.random() < 0.9 else random.choice(WORKSTATIONS)

    elif user["role"] == "admin":
        return random.choice(SERVERS + DOMAIN_CONTROLLERS + ADMIN_HOSTS)

    elif user["role"] == "tester":
        return random.choice(ALL_HOSTS)

    elif user["role"] == "system":
        return user["home_host"]

    return random.choice(WORKSTATIONS)


# -----------------------------
# IP POOL
# -----------------------------

OFFICE_IP_POOL = [f"10.0.0.{i}" for i in range(10, 200)]
REMOTE_IP_POOL = [f"192.168.1.{i}" for i in range(10, 200)]


def get_daily_ip(user):

    if user["role"] == "system":
        return None

    return random.choice(OFFICE_IP_POOL) if random.random() < 0.8 else random.choice(REMOTE_IP_POOL)


# -----------------------------
# TIME GENERATION
# -----------------------------

def generate_timestamp(user, day):

    if user["shift"] == "day":
        hour = random.choice(list(OFFICE_HOURS))

    elif user["shift"] == "night":
        hour = random.choice(list(range(18, 24)) + list(range(0, 6)))

    else:
        hour = random.randint(0, 23)

    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return START_DATE + timedelta(days=day, hours=hour, minutes=minute, seconds=second)


# -----------------------------
# EVENT GENERATION
# -----------------------------

def generate_event(user, ip, timestamp):

    event_id = random.choice(ALL_EVENTS)
    host = select_host(user)

    record = {
        "timestamp": timestamp,
        "event_id": event_id,
        "host": host,
        "user": user["name"],
        "role": user["role"],
        "is_tester": user["role"] == "tester",
        "event_category": None
    }

    if event_id in EVENTS_WITH_IP and ip:
        record["source_ip"] = ip

    if event_id == 4624:
        record["status"] = "success"
        record["logon_type"] = random.choice([2, 3, 10])
        record["event_category"] = "authentication"

    elif event_id == 4625:
        record["status"] = "failed"
        record["logon_type"] = random.choice([3, 10])
        record["event_category"] = "authentication"

    elif event_id == 4688:
        record["process"] = random.choice(PROCESS_LIST)
        record["event_category"] = "process_activity"

    elif event_id == 4672:
        record["privilege"] = "admin_assigned"
        record["event_category"] = "privilege_activity"

    elif event_id == 4634:
        record["status"] = "logoff"
        record["event_category"] = "authentication"

    elif event_id == 5058:
        record["crypto_op"] = "key_operation"
        record["event_category"] = "crypto_activity"

    elif event_id == 5061:
        record["crypto_op"] = "crypto_operation"
        record["event_category"] = "crypto_activity"

    return record


# -----------------------------
# TESTER LOGIN BURST
# -----------------------------

def generate_login_burst(user, day):

    logs = []

    burst_size = random.randint(50, 120)
    base_time = generate_timestamp(user, day)
    ip = get_daily_ip(user)

    for i in range(burst_size): #NOSONAR

        timestamp = base_time + timedelta(seconds=random.randint(0, 59))

        event_id = random.choice([4625, 4625, 4625, 4624])

        logs.append({
            "timestamp": timestamp,
            "event_id": event_id,
            "host": random.choice(ALL_HOSTS),
            "user": user["name"],
            "role": user["role"],
            "is_tester": True,
            "source_ip": ip,
            "logon_type": 3,
            "status": "failed" if event_id == 4625 else "success",
            "event_category": "authentication"
        })

    return logs


# -----------------------------
# MAIN GENERATOR
# -----------------------------

def generate_logs(total_events):

    users = generate_users()
    logs = []

    i = 0

    while i < total_events:

        user = random.choice(users)
        day = random.randint(0, DAYS - 1)

        if user["role"] == "tester" and random.random() < BURST_PROBABILITY:

            burst_logs = generate_login_burst(user, day)
            logs.extend(burst_logs)
            i += len(burst_logs)
            continue

        timestamp = generate_timestamp(user, day)
        ip = get_daily_ip(user)

        event = generate_event(user, ip, timestamp)

        logs.append(event)

        i += 1

        if i % 10000 == 0:
            print(f"Generated {i} events...")

    df = pd.DataFrame(logs)
    df.sort_values("timestamp", inplace=True) #NOSONAR

    df.to_csv("synthetic_windows_security_logs.csv", index=False)

    print("CSV generated successfully.")


# -----------------------------
# USER INPUT
# -----------------------------

if __name__ == "__main__":

    total = int(input("How many events do you want to generate? "))
    generate_logs(total)