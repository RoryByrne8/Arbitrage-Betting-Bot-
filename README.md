# Arbitrage-Betting-Bot
- Pulls in odds from different bookmakers via API
- Focuses on over/under football betting markets
- Checks pairwise odds of bookies to search for arbitarge opportunities due to mispricing between different bookies
- Uses async to check simulatenously rather than looping through each makret and bookie in order
- If arbitrage found, sends me text message through a telegram bot with all relevant market and bookie details
- I place bet
