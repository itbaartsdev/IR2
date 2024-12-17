import requests
import json
import time
from colorama import init, Fore, Style
import os
from datetime import datetime
import base64   

# Initialize colorama
init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def key_bot():
    api = base64.b64decode("aHR0cHM6Ly9pdGJhYXJ0cy5jb20vYXBpX3ByZW0uanNvbg==").decode('utf-8')
    try:
        response = requests.get(api)
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print('\033[96m' + f"Failed to load header: {e}" + '\033[0m')

class MissionBot:
    def __init__(self, token=None):
        self.base_url = "https://api.immortalrising2.com"
        if not token:
            raise ValueError("Bearer token is required!")
            
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Origin": "https://immortalrising2.com",
            "Referer": "https://immortalrising2.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

    def print_banner(self):
        clear_screen()
        key_bot()
        print(f"{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}         {Fore.WHITE}Welcome to IR2 Mission Bot{Style.RESET_ALL}         {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}▶ Bot Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")

    def log_message(self, message, type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if type == "info":
            print(f"{Fore.BLUE}[{timestamp}] ℹ {message}{Style.RESET_ALL}")
        elif type == "success":
            print(f"{Fore.GREEN}[{timestamp}] ✓ {message}{Style.RESET_ALL}")
        elif type == "error":
            print(f"{Fore.RED}[{timestamp}] ✗ {message}{Style.RESET_ALL}")
        elif type == "warning":
            print(f"{Fore.YELLOW}[{timestamp}] ⚠ {message}{Style.RESET_ALL}")

    def check_missions(self):
        try:
            response = requests.get(
                f"{self.base_url}/mission",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log_message(f"Error checking missions: {str(e)}", "error")
            return None

    def claim_mission(self, mission_id):
        try:
            payload = {"missionId": mission_id}
            response = requests.post(
                f"{self.base_url}/mission",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def auto_clear_missions(self):
        self.print_banner()
        self.log_message("Starting auto clear missions...", "info")
        retry_count = 0
        max_retries = 3

        while True:
            try:
                missions = self.check_missions()
                if not missions:
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.log_message("Failed to get mission data after several attempts.", "error")
                        break
                    self.log_message(f"Retrying in 10 seconds... (Attempt {retry_count}/{max_retries})", "warning")
                    time.sleep(10)
                    continue

                retry_count = 0
                
                # Filter semua misi yang belum diklaim
                unclaimed_missions = [
                    mission for mission in missions 
                    if not mission.get("claimed")
                ]

                if not unclaimed_missions:
                    self.log_message("All missions have been claimed!", "success")
                    break

                total_rewards = 0
                claimed_count = 0
                failed_count = 0

                for mission in unclaimed_missions:
                    self.log_message(f"Attempting to claim: {mission['title']} ({mission['rewardAmount']} orbs)", "info")
                    result = self.claim_mission(mission['id'])
                    
                    if result and result.get("message") == "Success":
                        total_rewards += mission['rewardAmount']
                        claimed_count += 1
                        self.log_message(f"Successfully claimed {mission['title']} - Reward: {mission['rewardAmount']} orb", "success")
                    else:
                        failed_count += 1
                        self.log_message(f"Failed to claim {mission['title']}", "error")
                    
                    time.sleep(2)
                
                # Tampilkan ringkasan
                self.log_message(f"Claiming session completed:", "info")
                self.log_message(f"Successfully claimed: {claimed_count} missions", "success")
                self.log_message(f"Failed to claim: {failed_count} missions", "warning")
                self.log_message(f"Total rewards earned: {total_rewards} orbs", "success")
                break
                    
            except Exception as e:
                self.log_message(f"Unexpected error: {str(e)}", "error")
                time.sleep(5)

def main():
    clear_screen()
    key_bot()
    print(f"{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}         {Fore.WHITE}Welcome to IR2 Mission Bot{Style.RESET_ALL}         {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    try:
        token = input(f"{Fore.YELLOW}Enter your Bearer token: {Style.RESET_ALL}").strip()
        bot = MissionBot(token)
        bot.auto_clear_missions()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Bot stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
