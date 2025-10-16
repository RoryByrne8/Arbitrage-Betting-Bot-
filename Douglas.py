import requests
import asyncio
import nest_asyncio
import aiohttp
import json
import pandas as pd
import time
from datetime import datetime

ODDS_API_KEY = "YOUR API KEY HERE"
ODDS_API_URL = " YOUR API URL HERE"

BOOKMAKERS = [
    "sport888",  
    "betfair_ex_uk",  
    "betfair_sb_uk",  
    "betvictor",  
    "betway",  
    "boylesports",  
    "casumo",  
    "coral",  
    "grosvenor",  
    "ladbrokes_uk",  
    "leovegas",  
    "livescorebet",  
    "matchbook",  
    "skybet",  
    "smarkets",  
    "unibet_uk",  
    "virginbet",  
    "williamhill",  
    
    # EU Bookies
    "onexbet",  
    "betclic",  
    "betanysports",  
    "betonlineag",  
    "betsson", 
    "coolbet",  
    "everygame",  
    "gtbets",  
    "marathonbet",  
    "mybookieag", 
    "nordicbet",  
    "pinnacle",  
    "suprabets",  
    "tipico_de",  
    "unibet_eu",  
    "winamax_de",  
    "winamax_fr",
]

#  Betting Market 
MARKET = "totals" 

# tgram bot
TELEGRAM_BOT_TOKEN = "YOUR TELEGRAM BOT TOKEN HERE"
TELEGRAM_CHAT_ID = "YOUR TELEGRAM CHAT ID HERE"


# Football Leagues to Monitor
FOOTBALL_LEAGUES = [
    "soccer_epl",  
    "soccer_uefa_champs_league", 
    "soccer_italy_serie_a",  
    "soccer_spain_la_liga",  
    "soccer_germany_bundesliga",  
    "soccer_france_ligue_one",  
    "soccer_international_friendly",  
    "soccer_fifa_world_cup",  
    "soccer_fifa_world_cup_womens",  
    "soccer_mls", 
    "soccer_uefa_europa_league",  
    "soccer_uefa_europa_conference_league",  
    "soccer_uefa_european_championship",  
    "soccer_uefa_euro_qualification",  
    "soccer_uefa_nations_league",  
    "soccer_conmebol_copa_america", 
    "soccer_conmebol_copa_libertadores",  
    "soccer_conmebol_copa_sudamericana",  
    "soccer_argentina_primera_division",  
    "soccer_australia_aleague",
    "soccer_austria_bundesliga",  
    "soccer_belgium_first_div",  
    "soccer_brazil_campeonato",  
    "soccer_brazil_serie_b",  
    "soccer_chile_campeonato",  
    "soccer_china_superleague",  
    "soccer_denmark_superliga",  
    "soccer_efl_champ",  
    "soccer_england_efl_cup",  
    "soccer_england_league1",  
    "soccer_england_league2",  
    "soccer_fa_cup",  
    "soccer_finland_veikkausliiga",  
    "soccer_germany_bundesliga2",  
    "soccer_germany_liga3",  
    "soccer_greece_super_league",  
    "soccer_japan_j_league", 
    "soccer_korea_kleague1", 
    "soccer_league_of_ireland",  
    "soccer_mexico_ligamx",  
    "soccer_netherlands_eredivisie",  
    "soccer_norway_eliteserien",  
    "soccer_poland_ekstraklasa",  
    "soccer_portugal_primeira_liga",  
    "soccer_spain_segunda_division",  
    "soccer_spl",  
    "soccer_sweden_allsvenskan",  
    "soccer_sweden_superettan",  
    "soccer_switzerland_superleague",  
    "soccer_turkey_super_league",  
]

def fetch_odds(league):
    ODDS_URL = f"https://api.the-odds-api.com/v4/sports/{league}/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "uk,eu", 
        "markets": MARKET,  # Only Over/Under
        "oddsFormat": "decimal",
        "bookmakers": ",".join(BOOKMAKERS)
    }

    response = requests.get(ODDS_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        
        available_bookmakers = set()
        for event in data:
            for bookmaker in event.get("bookmakers", []):
                available_bookmakers.add(bookmaker["key"])

        print(f"\n Available bookmakers in {league}: {available_bookmakers}")
        return data
    else:
        print(f" Error fetching odds for {league}: {response.status_code}")
        return None

# Detect Arbitrage Opportunities
def find_arbitrage(odds_data, league):
    arbitrage_opportunities = []

    if not odds_data:
        print(f" No odds data received for {league}.")
        return arbitrage_opportunities

    for event in odds_data:
        event_name = f"{event['home_team']} vs {event['away_team']}"
        under_odds = {}
        over_odds = {}

        print(f"\n Checking event: {event_name} ({league})")

        for bookmaker in event.get("bookmakers", []):
            bookie_name = bookmaker["key"]

            for market in bookmaker.get("markets", []):
                if market["key"] == "totals":  # Only Over/Under markets
                    for outcome in market["outcomes"]:
                        goal_line = outcome.get("point", "N/A")  

                        if "Under" in outcome["name"]:
                            under_odds[(bookie_name, goal_line)] = outcome["price"]
                            print(f"    Under {goal_line} @ {outcome['price']} ({bookie_name})")
                        
                        elif "Over" in outcome["name"]:
                            over_odds[(bookie_name, goal_line)] = outcome["price"]
                            print(f"     Over {goal_line} @ {outcome['price']} ({bookie_name})")

        # Compare Over and Under odds across different bookmakers
        for (bookie1, goal_line), under_price in under_odds.items():
            for (bookie2, goal_line2), over_price in over_odds.items():
                if goal_line == goal_line2 and bookie1 != bookie2:  #  Ensure matching goal lines
                    if check_arbitrage(under_price, over_price):
                        print(f"Arbitrage found: {event_name} - Over/Under {goal_line} Goals")
                        arbitrage_opportunities.append({
                            "event": event_name,
                            "league": league,
                            "goal_line": goal_line,
                            "bookie1": bookie1,
                            "bookie2": bookie2,
                            "outcome1": "Under",
                            "odds1": under_price,
                            "outcome2": "Over",
                            "odds2": over_price,
                            "stake_distribution": calculate_stakes(under_price, over_price)
                        })
                    else:
                        print(f" No arbitrage: Under {under_price} ({bookie1}) vs Over {over_price} ({bookie2})")

    return arbitrage_opportunities


# Arb check
def check_arbitrage(odds1, odds2):
    """Determine if an arbitrage opportunity exists."""
    arb_condition = (1 / odds1) + (1 / odds2)
   # print(f"   Arbitrage Formula: (1/{odds1}) + (1/{odds2}) = {round(arb_condition, 4)}")
    return arb_condition < 1

#  Stake calc
def calculate_stakes(odds1, odds2, total_stake=100):
    """Calculate optimal stake allocation for arbitrage."""
    stake1 = (total_stake / odds1) / ((1 / odds1) + (1 / odds2))
    stake2 = (total_stake / odds2) / ((1 / odds1) + (1 / odds2))
    return {"stake1": round(stake1, 2), "stake2": round(stake2, 2)}

#Send Telegram Alert
async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                print(f" Error sending Telegram message: {await response.text()}")

#  Continuous Arbitrage Scanner 
async def main():
    while True:
        for league in FOOTBALL_LEAGUES:
            print(f"\n Fetching totals odds for {league}...")
            odds_data = fetch_odds(league)

            if odds_data:
                print(f" Odds retrieved for {league}")
                opportunities = find_arbitrage(odds_data, league)

                if opportunities:
                    for opp in opportunities:
                        message = (
                            f" *Arbitrage Opportunity Found!*\n\n"
                            f" *League:* {opp['league']}\n"
                            f" *Match:* {opp['event']}\n"
                            f" *Market:* Over/Under {opp['goal_line']} Goals\n"
                            f" *{opp['outcome1']}* at {opp['bookie1']}: {opp['odds1']}\n"
                            f" *{opp['outcome2']}* at {opp['bookie2']}: {opp['odds2']}\n"
                            f" *Stake Distribution:*\n"
                            f"  - {opp['outcome1']}: ${opp['stake_distribution']['stake1']}\n"
                            f"  - {opp['outcome2']}: ${opp['stake_distribution']['stake2']}\n"
                        )
                        await send_telegram_message(message)
                else:
                    print(f" No arbitrage found for {league}")

        print("\n Waiting before next scan...\n")
        time.sleep(540)
        
#  Run the bot
if __name__ == "__main__":
    nest_asyncio.apply()  # Allow nested async loops in Jupyter
    asyncio.get_event_loop().run_until_complete(main())