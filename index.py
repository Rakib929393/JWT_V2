import json
import asyncio
import aiohttp
from colorama import Fore, Style, init
from pyfiglet import Figlet
from tqdm.asyncio import tqdm_asyncio
from datetime import datetime

init(autoreset=True)

class AsyncJWTCollector:
def init(self):
self.config = {
'source_file': 'token.json',
'output_file': 'token_bd.json',
'concurrent_tasks': 20,
'api_url': 'https://jwt-token-tau.vercel.app/get-token',
'timeout': 10
}
self.stats = {
'start_time': None,
'end_time': None,
'success': 0,
'failed': 0
}

async def display_banner(self):  
    f = Figlet(font='slant')  
    banner = f.renderText('JWT  HARVESTER')  
    print(Fore.CYAN + banner)  
    print(Fore.YELLOW + "✨ Advanced Async Token Collector")  
    print(Fore.MAGENTA + "=" * 60)  
    print(Fore.WHITE + "Developer: " + Fore.CYAN + "Shahadat Hassan")  
    print(Fore.WHITE + "Telegram: " + Fore.CYAN + "@pikachufrombd")  
    print(Fore.MAGENTA + "=" * 60)  
    print(Fore.WHITE + f"Source: {self.config['source_file']}")  
    print(Fore.WHITE + f"Output: {self.config['output_file']}")  
    print(Fore.WHITE + f"Concurrency: {self.config['concurrent_tasks']}")  
    print(Fore.MAGENTA + "=" * 60 + Style.RESET_ALL)  

async def load_credentials(self):  
    try:  
        with open(self.config['source_file'], 'r') as f:  
            return json.load(f)  
    except Exception as e:  
        print(Fore.RED + f"❌ Error loading {self.config['source_file']}: {str(e)}")  
        return None  

async def fetch_token(self, session, uid, password, semaphore):  
    url = f"{self.config['api_url']}?uid={uid}&password={password}"  
    try:  
        async with semaphore:  
            async with session.get(url, timeout=self.config['timeout']) as response:  
                data = await response.json()  
                if response.status == 200 and 'token' in data:  
                    return {'uid': uid, 'data': data, 'status': 'success'}  
                return {'uid': uid, 'status': f'failed_{response.status}'}  
    except Exception as e:  
        return {'uid': uid, 'status': f'error_{str(e)}'}  

async def process_tokens(self, credentials):  
    semaphore = asyncio.Semaphore(self.config['concurrent_tasks'])  
    connector = aiohttp.TCPConnector(limit=self.config['concurrent_tasks'])  
      
    async with aiohttp.ClientSession(connector=connector) as session:  
        tasks = [self.fetch_token(session, cred['uid'], cred['password'], semaphore)   
                for cred in credentials]  
        return await tqdm_asyncio.gather(*tasks, desc=Fore.YELLOW + "Collecting Tokens" + Style.RESET_ALL,   
                                      bar_format="{l_bar}{bar:20}{r_bar}")  

async def save_results(self, results):  
    successful_tokens = [{'token': r['data']['token']} for r in results if r['status'] == 'success']  
    with open(self.config['output_file'], 'w') as f:  
        json.dump(successful_tokens, f, indent=2)  
    return successful_tokens  

async def show_summary(self, results):  
    self.stats['end_time'] = datetime.now()  
    elapsed = (self.stats['end_time'] - self.stats['start_time']).total_seconds()  
      
    print(Fore.MAGENTA + "\n" + "=" * 60)  
    print(Fore.CYAN + "📊 COLLECTION SUMMARY")  
    print(Fore.MAGENTA + "=" * 60)  
    print(Fore.GREEN + f"✓ SUCCESS: {self.stats['success']}")  
    print(Fore.RED + f"✗ FAILED: {self.stats['failed']}")  
    print(Fore.BLUE + f"⏱ ELAPSED TIME: {elapsed:.2f} seconds")  
    print(Fore.YELLOW + f"📁 OUTPUT: {self.config['output_file']}")  
      
    if self.stats['failed'] > 0:  
        print(Fore.MAGENTA + "-" * 40)  
        print(Fore.YELLOW + "⚠ FAILURE DETAILS:")  
        errors = {}  
        for r in results:  
            if r['status'] != 'success':  
                errors[r['status']] = errors.get(r['status'], 0) + 1  
        for error, count in sorted(errors.items()):  
            print(Fore.RED + f"• {error.replace('_', ' ').title()}: {count}")  
      
    print(Fore.MAGENTA + "=" * 60 + Style.RESET_ALL)  

async def run(self):  
    await self.display_banner()  
    self.stats['start_time'] = datetime.now()  
      
    credentials = await self.load_credentials()  
    if not credentials:  
        return  
          
    results = await self.process_tokens(credentials)  
    successful_tokens = await self.save_results(results)  
      
    self.stats['success'] = len(successful_tokens)  
    self.stats['failed'] = len(results) - self.stats['success']  
      
    await self.show_summary(results)

if name == "main":
collector = AsyncJWTCollector()

try:  
    asyncio.run(collector.run())  
except KeyboardInterrupt:  
    print(Fore.RED + "\n🚫 Operation cancelled by user")  
except Exception as e:  
    print(Fore.RED + f"\n💥 Critical Error: {str(e)}")  
finally:  
    print(Fore.CYAN + "\n✨ Thank you for using JWT Harvester!" + Style.RESET_ALL)

