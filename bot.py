from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz
import re

class DePINed:
    def __init__(self) -> None:
        self.pkt = pytz.timezone('Asia/Karachi')
        self.BASE_API = "https://api.depined.org/api"
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.account_earnings = {}
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
        self.total_points = 0
        self.total_pings = 0
        self.last_update_id = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(self.pkt).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}DePINed {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "tokens.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            elif use_proxy_choice == 2:
                response = await asyncio.to_thread(requests.get, "https://gist.githubusercontent.com/SaeedX302/0c9c9850220784f8aebce1fde5759cf8/raw/efd8e2e7056080d334e2d422199f45d65d4da200/old-saeed.txt")
                response.raise_for_status()
                content = response.text
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    async def refresh_proxies(self):
        try:
            self.log(f"{Fore.YELLOW}Refreshing private proxies...{Style.RESET_ALL}")
            response = await asyncio.to_thread(requests.get, "https://gist.githubusercontent.com/SaeedX302/0c9c9850220784f8aebce1fde5759cf8/raw/efd8e2e7056080d334e2d422199f45d65d4da200/old-saeed.txt")
            response.raise_for_status()
            content = response.text
            self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            
            if self.proxies:
                self.log(f"{Fore.GREEN}Proxies refreshed successfully. New total: {len(self.proxies)}{Style.RESET_ALL}")
                self.account_proxies = {} # Clear existing assigned proxies
                self.proxy_index = 0
            else:
                self.log(f"{Fore.RED}Failed to refresh proxies. The new list is empty.{Style.RESET_ALL}")
                
        except Exception as e:
            self.log(f"{Fore.RED}Failed to refresh proxies: {e}{Style.RESET_ALL}")
            self.proxies = []


    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            hide_local = local[:3] + '*' * 3 + local[-3:]
            return f"{hide_local}@{domain}"

    def print_message(self, email, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
    
    def escape_markdown(self, text):
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    async def send_telegram_status(self, message, use_proxy: bool):
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            self.log(f"{Fore.RED}Telegram token or chat ID not set. Skipping Telegram notification.{Style.RESET_ALL}")
            return
        
        try:
            proxies = {"http":self.get_next_proxy_for_account("telegram_bot"), "https":self.get_next_proxy_for_account("telegram_bot")} if use_proxy else None
            url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': self.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'MarkdownV2'
            }
            response = await asyncio.to_thread(requests.post, url, data=payload, proxies=proxies, impersonate="chrome110", verify=False)
            response.raise_for_status()
            self.log(f"{Fore.GREEN}Telegram status sent successfully.{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED}Failed to send Telegram message: {e}{Style.RESET_ALL}")
    
    async def telegram_status_task(self, use_proxy: bool):
        while True:
            await asyncio.sleep(600)  # Wait for 10 miutes
            try:
                if use_proxy:
                    await self.refresh_proxies()
                
                # Fetch quote from API
                proxies = {"http":self.get_next_proxy_for_account("quotes_api"), "https":self.get_next_proxy_for_account("quotes_api")} if use_proxy else None
                quote_response = await asyncio.to_thread(requests.get, "https://quotes.tsunstudio.pw/api/quotes", proxies=proxies, impersonate="chrome110", verify=False)
                quote_response.raise_for_status()
                quote_data = quote_response.json()
                
                # Handle API response which might be a list
                if isinstance(quote_data, list) and quote_data:
                    first_quote = quote_data[0]
                else:
                    first_quote = quote_data

                quote = first_quote.get("quote", "Quote not found.")
                author = first_quote.get("author", "Unknown Author")
                
                # Prepare status message with markdown
                status_message = (
                    f"✨ *DePINed BOT Live Status* ✨\n\n"
                    f"```Total Accounts: {len(self.access_tokens)}```\n\n"
                    f"```Total Proxies: {len(self.proxies)}```\n\n"
                    f"```Total Pings: {self.total_pings}```\n"
                    f"```Total Points: {self.total_points:.2f}```\n\n"
                    f"```"
                    f"{quote}\n"
                    f"~{author}"
                    f"```"
                )
                
                await self.send_telegram_status(status_message, use_proxy)
            except Exception as e:
                self.log(f"{Fore.RED}Failed to send status update to Telegram: {e}{Style.RESET_ALL}")

    async def get_telegram_updates(self, use_proxy: bool, max_retries=5):
        for retry in range(max_retries):
            try:
                proxies = {"http": self.get_next_proxy_for_account("telegram_updates"), "https": self.get_next_proxy_for_account("telegram_updates")} if use_proxy else None
                url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/getUpdates"
                params = {'offset': self.last_update_id + 1, 'timeout': 30}
                response = await asyncio.to_thread(requests.get, url, params=params, proxies=proxies, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except requests.errors.RequestsError as e:
                self.log(f"{Fore.YELLOW}Retry {retry + 1}/{max_retries}: Failed to get Telegram updates: {e}{Style.RESET_ALL}")
                self.rotate_proxy_for_account("telegram_updates")
                await asyncio.sleep(5)
            except Exception as e:
                self.log(f"{Fore.RED}Failed to get Telegram updates: {e}{Style.RESET_ALL}")
                return None
        return None

    async def listen_telegram_commands(self, use_proxy: bool):
        while True:
            updates = await self.get_telegram_updates(use_proxy)
            if updates and updates.get('ok') and updates.get('result'):
                for update in updates.get('result'):
                    self.last_update_id = update['update_id']
                    message = update.get('message')
                    if message and message.get('chat') and str(message['chat']['id']) == self.TELEGRAM_CHAT_ID:
                        command = message.get('text', '').strip()
                        if command == '/help':
                            help_message = self.escape_markdown(
                                f"👋 Welcome to DePINed BOT!\n\n"
                                f"I am here to help you monitor your DePINed accounts.\n\n"
                                f"Here are the available commands:\n"
                                f"➡️ /help - Show this help message.\n"
                                f"➡️ /status - Show the current earnings for all your accounts.\n"
                                f"➡️ /summary - Show an overall summary of the bot's status.\n\n"
                                f"If you have any questions, feel free to open an issue on the GitHub repository."
                            )
                            await self.send_telegram_status(help_message, use_proxy)
                        elif command == '/status':
                            status_message = "✨ Accounts Live Status ✨\n\n"
                            
                            for email, data in self.account_earnings.items():
                                status_message += (
                                    f"```[ Account: {data['name']} - Status: Epoch {data['epoch']} - Earning: {data['earnings']:.2f} PTS ]```\n"
                                )
                            
                            await self.send_telegram_status(status_message, use_proxy)
                        elif command == '/summary':
                            quote = "کے لیے اتنا بھی مت گرو کہ وہ تمہیں گرا ہوا سمجھنے لگے۔"
                            author = "نامعلوم"
                            summary_message = (
                                f"✨ *DePINed BOT Live Status* ✨\n\n"
                                f"```Accounts: {len(self.access_tokens)}```\n\n"
                                f"```Proxies: {len(self.proxies)}```\n\n"
                                f"```Pings: {self.total_pings}```\n"
                                f"```Points: {self.total_points:.2f}```\n\n"
                                f"```"
                                f"{quote}\n"
                                f"~{author}"
                                f"```"
                            )
                            await self.send_telegram_status(summary_message, use_proxy)

            await asyncio.sleep(5)


    async def check_connection(self, email: str, proxy=None):
        url = "https://api.ipify.org?format=json"
        proxies = {"http":proxy, "https":proxy} if proxy else None
        await asyncio.sleep(3)
        try:
            response = await asyncio.to_thread(requests.get, url=url, proxies=proxies, timeout=30, impersonate="chrome110", verify=False)
            response.raise_for_status()
            return True
        except Exception as e:
            self.print_message(email, proxy, Fore.RED, f"Connection Not 200 OK: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            return None

    async def user_epoch_earning(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/stats/epoch-earnings"
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            await asyncio.sleep(5)
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    continue
                self.print_message(email, proxy, Fore.RED, f"GET Earning Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            
    async def user_send_ping(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/widget-connect"
        data = json.dumps({"connected":True})
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            await asyncio.sleep(5)
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    continue
                self.print_message(email, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                return None
            
    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            is_valid = await self.check_connection(email, proxy)
            if is_valid:
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)
            
    async def process_user_earning(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            earning = await self.user_epoch_earning(email, proxy)
            if earning and earning.get("code") == 200:
                epoch = earning.get("data", {}).get("epoch", "N/A")
                balance = earning.get("data", {}).get("earnings", 0)
                self.total_points += balance
                
                # Get short name for status
                account_name = email.split('@')[0]
                
                self.account_earnings[email] = {
                    "name": account_name,
                    "epoch": epoch,
                    "earnings": balance
                }

                self.print_message(email, proxy, Fore.WHITE, f"Epoch {epoch} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Earning: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{balance:.2f} PTS{Style.RESET_ALL}"
                )

            await asyncio.sleep(15 * 60)
            
    async def process_send_ping(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(self.pkt).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            ping = await self.user_send_ping(email, proxy)
            if ping and ping.get("message") == "Widget connection status updated":
                self.print_message(email, proxy, Fore.GREEN, "PING Success")
                self.total_pings += 1

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(self.pkt).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 90 Seconds For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(1.5 * 60)
        
    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(email, use_proxy, rotate_proxy)
        if is_valid:
            tasks = [
                asyncio.create_task(self.process_user_earning(email, use_proxy)),
                asyncio.create_task(self.process_send_ping(email, use_proxy))
            ]
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            tokens = self.load_accounts()
            if not tokens:
                self.log(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice = int(os.environ.get('PROXY_CHOICE', '3'))
            rotate_proxy = os.environ.get('ROTATE_PROXY', 'n').lower() == 'y'

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = [
                asyncio.create_task(self.telegram_status_task(use_proxy)),
                asyncio.create_task(self.listen_telegram_commands(use_proxy))
            ]
            for idx, account in enumerate(tokens, start=1):
                if account:
                    email = account["Email"]
                    token = account["accessToken"]
                    
                    # Store a shortened name for the status command
                    self.account_earnings[email] = {"name": email.split('@')[0], "epoch": "N/A", "earnings": 0}

                    if not "@" in email or not token:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.HEADERS[email] = {
                        "Accept": "*/*",
                        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Origin": "chrome-extension://pjlappmodaidbdjhmhifbnnmmkkicjoc",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "none",
                        "User-Agent": FakeUserAgent().random,
                        "X-Requested-With": "XMLHttpRequest"
                    }

                    self.access_tokens[email] = token

                    tasks.append(asyncio.create_task(self.process_accounts(email, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            if self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID:
                await self.send_telegram_status(f"🚨 **(Emergency)**\n\nBOT has stopped due to an error: {e}", use_proxy)
            raise e

if __name__ == "__main__":
    try:
        bot = DePINed()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(bot.pkt).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DePINed - BOT{Style.RESET_ALL}                                       "                              
        )