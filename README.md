# Arbitrage Betting Bot
- Pulls in odds from different bookmakers via API
- Focuses on over/under football betting markets
- Checks pairwise odds of bookies to search for arbitarge opportunities due to mispricing between different bookies
- Uses async to check simulatenously rather than looping through each makret and bookie in order
- If arbitrage found, sends me text message through a telegram bot with all relevant market and bookie details
- I place bet
- I named the bot Douglas


Potential Improvements:
The Odds API that is currently used has quite limited bookies and markets, finding a better API with the larger bookies such as Paddy Power and Bet 365 would be good.
Potentially could web scrape odds also but would have to be weary of throttling.
Automatic bet placement would be cool but I don't think many bookies have APIs that would let you do that 
