import asyncio
import argparse
import json
import sys

base_delay = 0.5
DEFAULT_REPORT_NAME = "report.json"


async def simulate_service(name: str, delay: float, attempt: int) -> dict:
    await asyncio.sleep(delay)
    return {"name": name, "status": "ok", "latency": delay, "attempts": attempt}


async def check_service(
        config: dict,
        timeout: float,
        max_retries: int,
        semaphore: asyncio.Semaphore,
        counter: list
) -> dict:
    attempt_index = 0
    name = config["name"]
    delay = config["delay"]

    for attempt_index in range(max_retries + 1):
        try:
            async with semaphore:
                async with asyncio.timeout(timeout):
                    result = await simulate_service(name, delay, attempt_index + 1)
                    counter[0] += 1
                    update_progress(counter[0], counter[1])
                    return result
        except (asyncio.TimeoutError, ConnectionError):
            if attempt_index == max_retries:
                break

            await asyncio.sleep(base_delay * (2 ** attempt_index))

    counter[0] += 1
    update_progress(counter[0], counter[1])
    return {"name": name, "status": "error", "latency": delay, "attempts": attempt_index + 1}


def update_progress(current: int, total: int):
    percent = (current / total) * 100
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    print(f"\rProgressbar: |{bar}| {percent:.1f}% ({current}/{total})", end="", flush=True)


async def check_services(configs: list, timeout: float, retries: int, concurrency: int):
    semaphore = asyncio.Semaphore(concurrency)
    counter = [0, len(configs)]

    tasks = [check_service(cfg, timeout, retries, semaphore, counter) for cfg in configs]
    return await asyncio.gather(*tasks)


def main():
    parser = argparse.ArgumentParser(description="Service Monitoring Tool CLI")
    parser.add_argument("--timeout", type=float, default=1.0, help="Timeout in seconds for one request")
    parser.add_argument("--retries", type=int, default=3, help="Attempt's count")
    parser.add_argument("--concurrency", type=int, default=2, help="Concurrency request's count")
    parser.add_argument("--output", action="store_true", help="Get JSON-report")

    args = parser.parse_args()

    print(f"Start running {len(service_configs)} services (concurrency={args.concurrency})...")

    results = asyncio.run(check_services(
        service_configs, args.timeout, args.retries, args.concurrency
    ))

    any_error = False
    for res in results:
        mark = "✔" if res["status"] == "ok" else "✘"
        if res["status"] == "error":
            any_error = True
        print(f"\n{mark} {res['name']}: {res['status']} ({res['latency']}s), attempt: {res['attempts']}", end="")

    if args.output:
        with open(DEFAULT_REPORT_NAME, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\n[INFO] The report is saved in {DEFAULT_REPORT_NAME}")

    if any_error:
        sys.exit(1)


if __name__ == "__main__":
    service_configs = [
        {"name": "Database", "delay": 0.5},
        {"name": "Auth-API", "delay": 2.5},
        {"name": "Cache", "delay": 0.1},
        {"name": "Storage", "delay": 1.2},
    ]

    main()
