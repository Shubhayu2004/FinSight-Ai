def recommending(df, global_polarity, today_stock, mean, quote):
    if today_stock.iloc[-1]['Close'] < mean:
        if global_polarity > 0:
            idea = "RISE"
            decision = "BUY"
            print()
            print("##############################################################################")
            print(f"According to the ML Predictions and Sentiment Analysis of Tweets, a {idea} in {quote} stock is expected => {decision}")
        elif global_polarity <= 0:
            idea = "FALL"
            decision = "SELL"
            print()
            print("##############################################################################")
            print(f"According to the ML Predictions and Sentiment Analysis of Tweets, a {idea} in {quote} stock is expected => {decision}")
    else:
        idea = "FALL"
        decision = "SELL"
        print()
        print("##############################################################################")
        print(f"According to the ML Predictions and Sentiment Analysis of Tweets, a {idea} in {quote} stock is expected => {decision}")
    return idea, decision
