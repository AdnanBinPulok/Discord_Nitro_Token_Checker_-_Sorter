import os
os.system("pip install -r requirements.txt")
import requests
import asyncio
import datetime
import random



base_url = "https://canary.discord.com/api/v10"

check_subscription_url = base_url + "/users/@me/billing/subscriptions"
check_nitro_boosts_slots_url = base_url + "/users/@me/guilds/premium/subscription-slots"

valid = []
invalid = []
nitro_unavailable = []
nitro_redeeemable = []

async def get_token_info(token,proxy=None):
    global valid_tokens, invalid
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    session = requests.Session()
    if proxy:
        session.proxies = proxy
    
    if headers:
        session.headers.update(headers)

    async def get_user_name():
        response = session.get(base_url + "/users/@me")
        if response.status_code == 200:
            user_name = response.json()["username"]
            return user_name
        else:
            return None
    
    data = {"token": token}

    user_name = await get_user_name()
    if not user_name:
        invalid.append(token)
        return
    else:
        data["user_name"] = user_name
    
    async def check_nitro():
        nitro_response = session.get(check_subscription_url)
        if nitro_response.status_code != 200:
            return
        nitro_data = nitro_response.json()
        if nitro_data:
            nitro_data = nitro_data[0]
            current_period_start = nitro_data.get('current_period_start') # 2024-01-29T15:48:18.555014+00:00
            current_period_end = nitro_data.get('current_period_end') # 2025-01-29T15:48:18.555014+00:00
            current_period_start = datetime.datetime.strptime(current_period_start, "%Y-%m-%dT%H:%M:%S.%f%z")
            current_period_end = datetime.datetime.strptime(current_period_end, "%Y-%m-%dT%H:%M:%S.%f%z")
            subscription_period_time = current_period_end - current_period_start
            subscription_type = "unknown"
            if subscription_period_time.days in [29,30,31]:
                subscription_type = "1 Month"
            elif subscription_period_time.days in [88,89,90,91,92,93]:
                subscription_type = "3 Months"
            elif subscription_period_time.days in [365,366]:
                subscription_type = "1 Year"
            else:
                subscription_type = "unknown"
            token_text = f"{subscription_type} Nitro"
            nitro_days_left = current_period_end - datetime.datetime.now(datetime.timezone.utc)
            sorted_nitro_left_in_days = f"{nitro_days_left.days} Days"

            return token_text,sorted_nitro_left_in_days
        else:
            return False
        
    nitro_available = await check_nitro()
    if not nitro_available:
        nitro_unavailable.append(token)
        return
    else:
        data["nitro"] = nitro_available[0]
        data["days_left"] = nitro_available[1]
    

    async def check_nitro_boosts():
        nitro_boosts_response = session.get(check_nitro_boosts_slots_url)
        if nitro_boosts_response.status_code != 200:
            return
        nitro_boosts_data = nitro_boosts_response.json()
        total_boosts = len(nitro_boosts_data)
        used_boosts = sum([1 for boost in nitro_boosts_data if boost.get("premium_guild_subscription")])
        
        return total_boosts,used_boosts
    
    nitro_boosts = await check_nitro_boosts()
    if not nitro_boosts:
        nitro_unavailable.append(token)
        return
    else:
        data["total_boosts"] = nitro_boosts[0]
        data["used_boosts"] = nitro_boosts[1]
    
    async def elligable_for_nitro_redeem():
        payments_response = session.get(base_url + "/users/@me/billing/payments")
        data = payments_response.json()
        successfull_payments = []
        for i in data:
            if i.get("payment_source"):
                if not i["payment_source"].get("invalid"):
                    successfull_payments.append(i)
        for data in successfull_payments:
            created_at = data.get("created_at")
            created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
            if created_at > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365):
                return False
        return True
    
    elligable_for_nitro_claim = await elligable_for_nitro_redeem()
    if elligable_for_nitro_claim:
        nitro_redeeemable.append(token)
        return
    
    valid.append(data)
    

with open("tokens.txt", "r") as file:
    tokens = file.read().splitlines()

with open("proxies.txt", "r") as file:
    proxies = file.read().splitlines()

if len(proxies) == 0:
    proxies = None
else:
    proxies = [{"http": f"http://{proxy}"} for proxy in proxies]

async def main():
    tasks = []
    for token in tokens:
        tasks.append(asyncio.create_task(get_token_info(token=token,proxy=random.choice(proxies) if proxies else None)))

    print("Checking Tokens. Please Wait...")
    await asyncio.gather(*tasks)
    

    sorted_valid_texts = [
        f"{'-'*100}\nUser Name: {data.get('user_name')}\nToken: {token}\nNitro: {data.get('nitro')}\nNitro Left: {data.get('days_left')}\nTotal Boosts: {data.get('total_boosts')}\nUsed Boosts: {data.get('used_boosts')}\nAvalable Boosts: {data.get('total_boosts')-data.get('used_boosts')}\n{'-'*100}" for data in valid
    ]

    print(f'\n\n'.join(sorted_valid_texts))

    if not os.path.exists("./outputs"):
        os.makedirs("./outputs")

    with open("./outputs/valid.txt", "w") as file:
        file.write("\n\n".join(sorted_valid_texts))
    with open("./outputs/invalid.txt", "w") as file:
        file.write("\n".join(invalid))
    with open("./outputs/nitro_unavailable.txt", "w") as file:
        file.write("\n".join(nitro_unavailable))
    with open("./outputs/nitro_redeeemable.txt", "w") as file:
        file.write("\n".join(nitro_redeeemable))

asyncio.run(main())
