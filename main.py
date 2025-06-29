#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage: python3 app1.py -n 1000000
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

def gen_schedule(agents, days):
    schedule = {}
    for agent in agents:
        schedule[agent] = {}
        for day in days:
            work_blocks = random.choice([[8], [4, 4], [2, 2, 2, 2]])
            blocks = []
            if random.random() < 0.5:
                start_hour = 9
            else:
                start_hour = 21 - sum(work_blocks)
            for block in work_blocks:
                start = start_hour
                end = start + block
                blocks.append({
                    'start': start if start != 9 else 0,
                    'end': end if end != 21 else 24,
                    'campaign': random.choice(CAMPAIGNS)
                })
                start_hour += block
            schedule[agent][day] = blocks
    return schedule

def get_agents(schedule, campaign, day, hour):
    agents = []
    for agent, days in schedule.items():
        if day in days:
            for block in days[day]:
                if block['campaign'] == campaign and block['start'] <= hour < block['end']:
                    agents.append(agent)
    return agents

def get_time(day):
    day_obj = datetime.strptime(day, '%Y-%m-%d')
    start_time = datetime.combine(day_obj, datetime.strptime('08:50', '%H:%M').time())
    end_time = datetime.combine(day_obj, datetime.strptime('21:10', '%H:%M').time())
    random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
    return start_time + timedelta(seconds=random_seconds)

def gen_status(campaign):
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

def gen_amount(status):
    if status in SALE_STATUSES:
        if random.random() < 0.005:
            return None
        return random.choice(range(0, 105, 5))
    return ''

def gen_calls(day, calls_n, schedule):
    calls = []
    for _ in range(calls_n):
        call_time = get_time(day)
        if random.random() < 0.7:
            campaign = random.choice(CAMPAIGNS[:-2])
        else:
            campaign = random.choice(CAMPAIGNS[-2:])
        # agent = random.choice(AGENTS)
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

def main(calls_total):
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday() + 7)
    days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
    print(days)
    schedule = gen_schedule(AGENTS, days)

    calls_by_days = np.full(5, calls_total // 5)
    for i in range(calls_total % 5):
        calls_by_days[i] += 1

    dfs = []
    for day, calls in zip(days, calls_by_days):
        df = gen_calls(day, calls, schedule)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    df.to_csv('calls.csv', index=False)
    print(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate call records CSV.')
    parser.add_argument('-n', type=int, required=True, help='Number of rows to generate')
    args = parser.parse_args()

    main(args.n)

