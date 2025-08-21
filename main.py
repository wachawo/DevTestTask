#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage: python3 app1.py --rows 1000000
"""
import argparse
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

CAMPAIGNS = [1000, 2000, 3000, 4000, 5000, 9000]
AGENTS = [f'agent{i:04d}' for i in range(1, 1001)]
STATUSES = ['CREDIT', 'SALE', 'DNC', 'NI', 'BUSY']
SALE_STATUSES = ['CREDIT', 'SALE']


def gen_schedule(agents: list[str], days: list[str]) -> dict[str, dict[str, list[dict]]]:
    schedule: dict[str, dict[str, list[dict]]] = {}
    for agent in agents:
        schedule[agent] = {}
        for day_str in days:
            work_blocks = random.choice([[8], [4, 4], [2, 2, 2, 2]])
            blocks: list[dict] = []
            if random.random() < 0.5:
                start_hour = 9
            else:
                start_hour = 21 - sum(work_blocks)
            for block_len in work_blocks:
                start = start_hour
                end = start + block_len
                blocks.append({
                    'start': start if start != 9 else 0,
                    'end': end if end != 21 else 24,
                    'campaign': random.choice(CAMPAIGNS)
                })
                start_hour += block_len
            schedule[agent][day_str] = blocks
    return schedule


def get_agents(schedule: dict[str, dict[str, list[dict]]], campaign: int, day: str, hour: int) -> list[str]:
    agents: list[str] = []
    for agent, agent_days in schedule.items():
        if day in agent_days:
            for block in agent_days[day]:
                if block['campaign'] == campaign and block['start'] <= hour < block['end']:
                    agents.append(agent)
    return agents


def get_time(day: str) -> datetime:
    day_obj = datetime.strptime(day, '%Y-%m-%d')
    start_time = datetime.combine(day_obj, datetime.strptime('08:50', '%H:%M').time())
    end_time = datetime.combine(day_obj, datetime.strptime('21:10', '%H:%M').time())
    random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
    return start_time + timedelta(seconds=random_seconds)


def gen_status(campaign: int) -> str | None:
    empty_chance = random.random()
    if empty_chance < 0.005:
        return None
    if campaign in CAMPAIGNS[-2:]:
        sale_weight = 10.0
    else:
        sale_weight = 4.0
    n_sale = len(SALE_STATUSES)
    n = len(STATUSES)
    other_weight = (100.0 - sale_weight) / (n - 2)
    weights = [sale_weight / n_sale] * n_sale + [other_weight] * (n - n_sale)
    return random.choices(STATUSES, weights=weights)[0]


def gen_amount(status: str | None) -> int | None | str:
    if status in SALE_STATUSES:
        if random.random() < 0.005:
            return None
        return random.choice(range(0, 105, 5))
    return ''


def gen_calls(day: str, rows: int, schedule: dict[str, dict[str, list[dict]]]) -> pd.DataFrame:
    calls: list[dict] = []
    for _ in range(rows):
        call_time = get_time(day)
        if random.random() < 0.7:
            campaign = random.choice(CAMPAIGNS[:-2])
        else:
            campaign = random.choice(CAMPAIGNS[-2:])
        agents = get_agents(schedule, campaign, day, call_time.hour)
        if agents:
            agent = random.choice(agents)
            status = gen_status(campaign)
            amount = gen_amount(status)
            calls.append({
                "CALLTIME": call_time.strftime("%Y-%m-%d %H:%M:%S"),
                "AGENT": agent,
                "CAMPAIGN": campaign,
                "STATUS": status,
                "AMOUNT": amount,
            })
        else:
            calls.append({
                "CALLTIME": call_time.strftime("%Y-%m-%d %H:%M:%S"),
                "AGENT": None,
                "CAMPAIGN": campaign,
                "STATUS": "NA",
                "AMOUNT": None,
            })
    return pd.DataFrame(calls)


def main(rows: int, csv_file: str = 'calls.csv') -> None:
    print(f"Generating {rows} calls and saving to {csv_file}...")
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday() + 7)
    days: list[str] = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
    print(days)
    schedule = gen_schedule(AGENTS, days)

    calls_by_days = np.full(5, rows // 5)
    for i in range(rows % 5):
        calls_by_days[i] += 1

    dfs: list[pd.DataFrame] = []
    for day_str, calls_count in zip(days, calls_by_days):
        df = gen_calls(day_str, int(calls_count), schedule)
        dfs.append(df)
    df_all = pd.concat(dfs, ignore_index=True)
    df_all.to_csv(csv_file, index=False)
    print(f"Generated {len(df_all.index)} calls and saved to {csv_file}.")
    print(df_all)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate call records CSV.')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows to generate')
    parser.add_argument('--csv_file', type=str, default='calls.csv', help='Output CSV file name')
    args = parser.parse_args()
    main(args.rows, csv_file=args.csv_file)
