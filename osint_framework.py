# -*- coding: utf-8 -*-
import requests
import json
import re
import time
import os
import hashlib
import socket
import base64
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings()

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'

def print_banner():
    print(f"""{Colors.CYAN}
    ╔══════════════════════════════════════════════╗
    ║        OSINT FRAMEWORK v5.0                  ║
    ║   Глубокий поиск + Утечки + Даркнет           ║
    ╚══════════════════════════════════════════════╝
    {Colors.RESET}""")

class DeepOSINT:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
        })
        self.timeout = 20
        self.found_data = []
    
    def _get(self, url, headers=None, cookies=None):
        try:
            if headers:
                self.session.headers.update(headers)
            resp = self.session.get(url, timeout=self.timeout, verify=False, cookies=cookies)
            return resp
        except:
            return None
    
    def _post(self, url, data=None, json_data=None):
        try:
            if json_data:
                resp = self.session.post(url, json=json_data, timeout=self.timeout, verify=False)
            else:
                resp = self.session.post(url, data=data, timeout=self.timeout, verify=False)
            return resp
        except:
            return None
    
    # ============================================================
    # ПОИСК EMAIL ВО ВСЕХ ИСТОЧНИКАХ
    # ============================================================
    
    def search_email(self, email):
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}  📧 ГЛУБОКИЙ ПОИСК EMAIL: {Colors.GREEN}{email}{Colors.RESET}")
        print(f"{'═' * 70}")
        
        domain = email.split('@')[1] if '@' in email else ''
        username = email.split('@')[0] if '@' in email else ''
        
        all_findings = []
        
        # 1. Have I Been Pwned
        print(f"\n  {Colors.CYAN}[1/15] Have I Been Pwned (утечки){Colors.RESET}")
        hibp = self._check_hibp(email)
        if hibp:
            all_findings.append(('HIBP', hibp))
        
        # 2. Dehashed (поиск по утечкам)
        print(f"\n  {Colors.CYAN}[2/15] Dehashed (база утечек){Colors.RESET}")
        dehashed = self._search_dehashed(email)
        if dehashed:
            all_findings.append(('Dehashed', dehashed))
        
        # 3. Snusbase
        print(f"\n  {Colors.CYAN}[3/15] Snusbase{Colors.RESET}")
        snusbase = self._search_snusbase(email)
        if snusbase:
            all_findings.append(('Snusbase', snusbase))
        
        # 4. LeakCheck
        print(f"\n  {Colors.CYAN}[4/15] LeakCheck{Colors.RESET}")
        leakcheck = self._search_leakcheck(email)
        if leakcheck:
            all_findings.append(('LeakCheck', leakcheck))
        
        # 5. Psbdmp
        print(f"\n  {Colors.CYAN}[5/15] Psbdmp (пароли){Colors.RESET}")
        psbdmp = self._search_psbdmp(email)
        if psbdmp:
            all_findings.append(('Psbdmp', psbdmp))
        
        # 6. Gravatar
        print(f"\n  {Colors.CYAN}[6/15] Gravatar (профиль){Colors.RESET}")
        gravatar = self._check_gravatar(email)
        if gravatar:
            all_findings.append(('Gravatar', gravatar))
        
        # 7. EmailRep
        print(f"\n  {Colors.CYAN}[7/15] EmailRep{Colors.RESET}")
        self._check_emailrep(email)
        
        # 8. Hunter.io
        print(f"\n  {Colors.CYAN}[8/15] Hunter.io (email по домену){Colors.RESET}")
        if domain:
            self._search_hunter(domain, email)
        
        # 9. Google поиск
        print(f"\n  {Colors.CYAN}[9/15] Google Dork поиск{Colors.RESET}")
        google = self._google_deep_search(email)
        if google:
            all_findings.append(('Google', google))
        
        # 10. GitHub поиск
        print(f"\n  {Colors.CYAN}[10/15] GitHub поиск{Colors.RESET}")
        github = self._search_github_code(email)
        if github:
            all_findings.append(('GitHub', github))
        
        # 11. Pastebin
        print(f"\n  {Colors.CYAN}[11/15] Pastebin{Colors.RESET}")
        pastebin = self._search_pastebin(email)
        if pastebin:
            all_findings.append(('Pastebin', pastebin))
        
        # 12. IntelX
        print(f"\n  {Colors.CYAN}[12/15] IntelX (даркнет){Colors.RESET}")
        intelx = self._search_intelx(email)
        if intelx:
            all_findings.append(('IntelX', intelx))
        
        # 13. Telegram поиск
        print(f"\n  {Colors.CYAN}[13/15] Telegram поиск{Colors.RESET}")
        self._search_telegram_channels(email)
        
        # 14. breachdirectory
        print(f"\n  {Colors.CYAN}[14/15] BreachDirectory{Colors.RESET}")
        breachdir = self._search_breachdirectory(email)
        if breachdir:
            all_findings.append(('BreachDirectory', breachdir))
        
        # 15. Firefox Monitor
        print(f"\n  {Colors.CYAN}[15/15] Firefox Monitor{Colors.RESET}")
        firefox = self._search_firefox_monitor(email)
        if firefox:
            all_findings.append(('FirefoxMonitor', firefox))
        
        # Итог
        print(f"\n  {Colors.BOLD}{'═' * 50}{Colors.RESET}")
        total = len(all_findings)
        if total > 0:
            print(f"  {Colors.RED}⚠ НАЙДЕНО В {total} ИСТОЧНИКАХ!{Colors.RESET}")
            for source, data in all_findings:
                print(f"    {Colors.RED}● {source}{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}Email не найден в утечках{Colors.RESET}")
            print(f"  Возможно email новый или не участвовал в утечках")
        
        self.results = {'email': email, 'sources': all_findings}
        return all_findings
    
    def _check_hibp(self, email):
        """Have I Been Pwned - самая большая база утечек"""
        findings = []
        try:
            # Основной поиск
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            resp = self.session.get(url, timeout=15, headers={'hibp-api-key': ''})
            
            if resp.status_code == 200:
                breaches = resp.json()
                print(f"    {Colors.RED}⚠ НАЙДЕН В {len(breaches)} УТЕЧКАХ!{Colors.RESET}")
                
                for b in breaches:
                    name = b.get('Name', 'Unknown')
                    domain = b.get('Domain', '')
                    date = b.get('BreachDate', '?')
                    desc = b.get('Description', '')[:150]
                    data_classes = b.get('DataClasses', [])
                    pwn_count = b.get('PwnCount', 0)
                    
                    print(f"    {Colors.RED}● {name}{Colors.RESET}")
                    print(f"      Дата: {date} | Записей: {pwn_count:,}")
                    print(f"      Утекло: {', '.join(data_classes)}")
                    
                    findings.append({
                        'source': name,
                        'date': date,
                        'records': pwn_count,
                        'data_types': data_classes,
                        'description': desc
                    })
            
            elif resp.status_code == 404:
                print(f"    {Colors.GREEN}Не найден в HIBP{Colors.RESET}")
            
            # Проверка паролей (Pwned Passwords)
            # Проверяем хвост хеша пароля
        
        except Exception as e:
            print(f"    Ошибка: {e}")
        
        return findings if findings else None
    
    def _search_dehashed(self, email):
        """Dehashed - крупнейшая база утечек"""
        findings = []
        try:
            # Поиск через API (требует API ключ, но можно пробовать)
            url = f"https://api.dehashed.com/search?query={email}"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                entries = data.get('entries', [])
                if entries:
                    print(f"    {Colors.RED}⚠ Найдено {len(entries)} записей!{Colors.RESET}")
                    for entry in entries[:10]:
                        db = entry.get('database_name', '?')
                        print(f"    {Colors.RED}● {db}{Colors.RESET}")
                        findings.append({'database': db, 'entry': entry})
            else:
                print(f"    Требуется API ключ (dehashed.com)")
        
        except:
            # Пробуем через веб-интерфейс
            try:
                url = f"https://www.dehashed.com/search?query={email}"
                resp = self._get(url)
                if resp and 'results' in resp.text.lower():
                    print(f"    {Colors.GREEN}Возможно найдены результаты{Colors.RESET}")
                    print(f"    Проверь: {url}")
            except:
                pass
        
        return findings if findings else None
    
    def _search_snusbase(self, email):
        """Snusbase - поиск по утечкам"""
        print(f"    Проверка...")
        try:
            url = f"https://snusbase.com/search?q={email}"
            resp = self._get(url)
            if resp and resp.status_code == 200:
                print(f"    Проверь вручную: {Colors.BLUE}{url}{Colors.RESET}")
        except:
            pass
        return None
    
    def _search_leakcheck(self, email):
        """LeakCheck API"""
        findings = []
        try:
            url = f"https://leakcheck.io/api/public?check={urllib.parse.quote(email)}"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                if data.get('success') and data.get('sources'):
                    sources = data['sources']
                    print(f"    {Colors.RED}⚠ Найден в {len(sources)} базах!{Colors.RESET}")
                    for s in sources[:10]:
                        print(f"    {Colors.RED}● {s}{Colors.RESET}")
                        findings.append({'source': s})
                else:
                    print(f"    Не найден")
        except:
            print(f"    Сервис недоступен")
        
        return findings if findings else None
    
    def _search_psbdmp(self, email):
        """Psbdmp - реальные пароли из утечек"""
        findings = []
        try:
            url = f"https://psbdmp.ws/api/v3/search/{urllib.parse.quote(email)}"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                count = data.get('count', 0)
                
                if count > 0:
                    print(f"    {Colors.RED}⚠ Найдено {count} записей с паролями!{Colors.RESET}")
                    
                    for item in data.get('data', [])[:5]:
                        text = item.get('text', '')
                        date = item.get('date', '')
                        url_paste = item.get('url', '')
                        
                        # Ищем строки с email и паролем
                        lines = text.split('\n')
                        for line in lines:
                            if email.lower() in line.lower():
                                # Очищаем строку
                                clean = line.strip()[:200]
                                print(f"    {Colors.RED}● [{date}] {clean[:120]}{Colors.RESET}")
                                findings.append({
                                    'date': date,
                                    'line': clean,
                                    'url': url_paste
                                })
                else:
                    print(f"    Не найден в Psbdmp")
        except:
            print(f"    Сервис недоступен")
        
        return findings if findings else None
    
    def _check_gravatar(self, email):
        """Gravatar - информация профиля"""
        try:
            email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
            
            # JSON профиль
            url = f"https://www.gravatar.com/{email_hash}.json"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                if 'entry' in data and data['entry']:
                    entry = data['entry'][0]
                    
                    print(f"    {Colors.GREEN}Gravatar НАЙДЕН!{Colors.RESET}")
                    
                    info = {}
                    
                    if 'displayName' in entry:
                        info['name'] = entry['displayName']
                        print(f"    Имя: {entry['displayName']}")
                    
                    if 'profileUrl' in entry:
                        info['profile_url'] = entry['profileUrl']
                        print(f"    Профиль: {entry['profileUrl']}")
                    
                    if 'currentLocation' in entry:
                        info['location'] = entry['currentLocation']
                        print(f"    Локация: {entry['currentLocation']}")
                    
                    if 'aboutMe' in entry:
                        info['bio'] = entry['aboutMe'][:150]
                        print(f"    Bio: {entry['aboutMe'][:120]}")
                    
                    if 'jobTitle' in entry:
                        info['job'] = entry['jobTitle']
                        print(f"    Работа: {entry['jobTitle']}")
                    
                    if 'company' in entry:
                        info['company'] = entry['company']
                        print(f"    Компания: {entry['company']}")
                    
                    # Связанные аккаунты
                    if 'accounts' in entry:
                        print(f"    Связанные аккаунты:")
                        for acc in entry['accounts'][:15]:
                            domain = acc.get('domain', '')
                            display = acc.get('display', '')
                            acc_url = acc.get('url', '')
                            print(f"      {Colors.BLUE}{domain}: {display}{Colors.RESET}")
                            if 'url' in acc:
                                print(f"        {acc['url']}")
                    
                    if 'urls' in entry:
                        print(f"    Ссылки:")
                        for u in entry['urls'][:10]:
                            print(f"      {u.get('title', '')}: {u.get('value', '')}")
                    
                    # Фото
                    avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=500"
                    print(f"    Фото: {avatar_url}")
                    
                    return info
            else:
                print(f"    Gravatar не найден")
        except Exception as e:
            print(f"    Ошибка: {e}")
        
        return None
    
    def _check_emailrep(self, email):
        """EmailRep - проверка репутации"""
        try:
            url = f"https://emailrep.io/{email}?summary=true"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                
                rep = data.get('reputation', 'unknown')
                details = data.get('details', {})
                
                print(f"    Репутация: {Colors.RED if rep == 'high' else Colors.GREEN}{rep}{Colors.RESET}")
                print(f"    Утечка паролей: {Colors.RED if details.get('credentials_leaked') else Colors.GREEN}{details.get('credentials_leaked', False)}{Colors.RESET}")
                print(f"    Подозрительный: {details.get('suspicious', False)}")
                print(f"    Спам: {details.get('spam', False)}")
                print(f"    Blacklist: {details.get('blacklisted', False)}")
                
                profiles = details.get('profiles', [])
                if profiles:
                    print(f"    Профили: {', '.join(profiles[:15])}")
                
                # Дата последнего замечения
                last_seen = details.get('last_seen', '')
                if last_seen:
                    print(f"    Последняя активность: {last_seen}")
        except:
            print(f"    Сервис недоступен")
    
    def _search_hunter(self, domain, email):
        """Hunter.io - поиск email по домену"""
        try:
            # Бесплатный поиск через веб
            url = f"https://hunter.io/search/{domain}"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                # Ищем email в ответе
                emails_found = re.findall(r'[\w\.-]+@' + re.escape(domain), resp.text)
                if emails_found:
                    unique = list(set(emails_found))
                    print(f"    {Colors.GREEN}Найдено {len(unique)} email на домене:{Colors.RESET}")
                    for e in unique[:10]:
                        print(f"    {e}")
        except:
            print(f"    Требуется API ключ hunter.io")
    
    def _google_deep_search(self, email):
        """Глубокий поиск в Google"""
        findings = []
        queries = [
            f'"{email}"',
            f'"{email}" password OR pass OR pwd',
            f'"{email}" site:pastebin.com',
            f'"{email}" site:github.com',
            f'"{email}" leak OR breach OR hacked OR database',
            f'"{email}" filetype:txt OR filetype:csv OR filetype:sql',
        ]
        
        print(f"    Сгенерировано {len(queries)} поисковых запросов")
        
        for query in queries[:2]:  # Проверяем первые 2
            try:
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=20"
                resp = self._get(url)
                
                if resp:
                    # Считаем результаты
                    match = re.search(r'About ([\d,]+) results', resp.text)
                    if match:
                        count = int(match.group(1).replace(',', ''))
                        if count > 0:
                            print(f"    Запрос '{query[:50]}...': {Colors.GREEN}{count:,} результатов{Colors.RESET}")
                            findings.append({'query': query, 'results': count})
                    
                    # Собираем ссылки
                    links = re.findall(r'href="(https?://[^"]+)"', resp.text)
                    real_links = [l for l in links if 'google.com' not in l][:5]
                    for link in real_links:
                        print(f"    {Colors.BLUE}{link[:100]}{Colors.RESET}")
                
                time.sleep(1)
            except:
                pass
        
        return findings if findings else None
    
    def _search_github_code(self, email):
        """Поиск в GitHub коде"""
        findings = []
        try:
            url = f"https://api.github.com/search/code?q={urllib.parse.quote(email)}&per_page=10"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                items = data.get('items', [])
                
                if items:
                    print(f"    {Colors.RED}⚠ Найдено {data.get('total_count', 0)} упоминаний в коде!{Colors.RESET}")
                    for item in items[:5]:
                        repo = item.get('repository', {}).get('full_name', '?')
                        path = item.get('path', '?')
                        html_url = item.get('html_url', '')
                        print(f"    {Colors.RED}● {repo}/{path}{Colors.RESET}")
                        print(f"      {html_url}")
                        findings.append({'repo': repo, 'path': path, 'url': html_url})
                else:
                    print(f"    Не найден в GitHub")
        except:
            print(f"    GitHub API лимит исчерпан")
        
        return findings if findings else None
    
    def _search_pastebin(self, email):
        """Поиск в Pastebin"""
        print(f"    Поиск через Google:")
        queries = [
            f'site:pastebin.com "{email}"',
            f'site:pastebin.com "{email}" password',
        ]
        for q in queries:
            encoded = urllib.parse.quote(q)
            print(f"    {Colors.BLUE}https://www.google.com/search?q={encoded}{Colors.RESET}")
        
        return None
    
    def _search_intelx(self, email):
        """IntelX - поиск в даркнете"""
        print(f"    IntelX поиск:")
        encoded = urllib.parse.quote(email)
        print(f"    {Colors.BLUE}https://intelx.io/?s={encoded}{Colors.RESET}")
        print(f"    (требуется регистрация, но дает доступ к даркнету)")
        return None
    
    def _search_telegram_channels(self, email):
        """Поиск в Telegram каналах и ботах"""
        print(f"    Боты для поиска:")
        bots = [
            '@UniversalSearchRobot - поиск по всем базам',
            '@EyeGodBot - поиск по утечкам',
            '@QuickOSINT_bot - OSINT поиск',
            '@TgAnalyst_bot - анализ профиля',
            '@LeakCheckBot - утечки и пароли',
            '@PasswordSearchBot - поиск паролей',
        ]
        for bot in bots:
            print(f"    {Colors.GREEN}{bot}{Colors.RESET}")
        
        # Ссылка на поиск в Telegram
        encoded = urllib.parse.quote(email)
        print(f"\n    Поиск в Telegram: {Colors.BLUE}https://t.me/search?q={encoded}{Colors.RESET}")
    
    def _search_breachdirectory(self, email):
        """BreachDirectory.org"""
        try:
            url = f"https://breachdirectory.org/api?func=auto&term={urllib.parse.quote(email)}"
            resp = self._get(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                if data.get('result'):
                    results = data['result']
                    print(f"    {Colors.RED}⚠ Найдено в BreachDirectory!{Colors.RESET}")
                    
                    for r in results[:10]:
                        has_password = 'password' in r
                        sources = r.get('sources', [])
                        print(f"    {Colors.RED}● Источники: {', '.join(sources)}{Colors.RESET}")
                        if has_password:
                            print(f"      Есть пароль!")
                    
                    return results
                else:
                    print(f"    Не найден")
        except:
            print(f"    Сервис недоступен")
        
        return None
    
    def _search_firefox_monitor(self, email):
        """Firefox Monitor (тот же HIBP но с доп информацией)"""
        try:
            email_hash = hashlib.sha1(email.lower().encode()).hexdigest().upper()
            prefix = email_hash[:6]
            
            url = f"https://monitor.firefox.com/api/v1/scan"
            resp = self._post(url, json_data={'email': email})
            
            if resp and resp.status_code == 200:
                data = resp.json()
                breaches = data.get('breaches', [])
                if breaches:
                    print(f"    {Colors.RED}⚠ Firefox Monitor: найдено {len(breaches)} утечек{Colors.RESET}")
                    return breaches
        except:
            pass
        
        print(f"    Проверь: https://monitor.firefox.com/")
        return None
    
    # ============================================================
    # ПОИСК ПО ТЕЛЕФОНУ
    # ============================================================
    
    def search_phone(self, phone):
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}  📱 ПОИСК ТЕЛЕФОНА: {Colors.GREEN}{phone}{Colors.RESET}")
        print(f"{'═' * 70}")
        
        phone_clean = re.sub(r'[^\d]', '', phone)
        
        if phone_clean.startswith('7') and len(phone_clean) == 11:
            code = phone_clean[1:4]
            operators = {
                '900': 'МТС', '901': 'МТС', '903': 'Билайн', '905': 'Билайн',
                '906': 'Билайн', '909': 'Билайн', '910': 'МТС', '916': 'МТС',
                '920': 'МегаФон', '921': 'МегаФон', '925': 'МегаФон',
                '926': 'МегаФон', '950': 'Tele2', '952': 'Tele2',
                '960': 'Билайн', '965': 'Билайн', '980': 'МТС',
            }
            operator = operators.get(code, 'Неизвестный')
            
            print(f"\n    Страна: Россия (+7)")
            print(f"    Код: {code}")
            print(f"    Оператор: {operator}")
        
        print(f"\n  {Colors.CYAN}[*] Поиск во всех источниках:{Colors.RESET}")
        
        # NumVerify
        try:
            url = f"http://apilayer.net/api/validate?access_key=demo&number={phone_clean}&country_code=RU"
            resp = self._get(url)
            if resp:
                data = resp.json()
                if data.get('valid'):
                    print(f"    Номер валиден: {data.get('local_format', '?')}")
                    print(f"    Оператор: {data.get('carrier', '?')}")
                    print(f"    Тип: {data.get('line_type', '?')}")
                    print(f"    Локация: {data.get('location', '?')}")
        except:
            pass
        
        # Поисковые запросы
        print(f"\n    Google поиск:")
        queries = [
            f'"{phone_clean}"',
            f'"{phone_clean}" vk OR telegram OR whatsapp',
            f'"{phone_clean}" site:avito.ru OR site:youla.ru',
            f'"{phone_clean}" site:vk.com',
        ]
        for q in queries:
            url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
            print(f"    {Colors.BLUE}{url}{Colors.RESET}")
        
        # Мессенджеры
        print(f"\n    Мессенджеры:")
        print(f"    WhatsApp: https://wa.me/{phone_clean}")
        print(f"    Telegram: https://t.me/+{phone_clean}")
        print(f"    Viber: viber://chat?number=%2B{phone_clean}")
        
        # Специализированные сервисы
        print(f"\n    Сервисы поиска:")
        print(f"    {Colors.BLUE}https://numverify.com/{Colors.RESET} - проверка номера")
        print(f"    {Colors.BLUE}https://phoneradar.com/{Colors.RESET} - информация о номере")
        print(f"    {Colors.BLUE}https://callinsider.com/{Colors.RESET} - жалобы на номер")
    
    def show_telegram_osint(self):
        """Полный гайд по Telegram OSINT"""
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}  🤖 TELEGRAM OSINT - ПОЛНЫЙ ГАЙД{Colors.RESET}")
        print(f"{'═' * 70}")
        
        print(f"""
{Colors.BOLD}Поисковые боты:{Colors.RESET}
{Colors.GREEN}@UniversalSearchRobot{Colors.RESET} - Поиск по ВСЕМ базам утечек
{Colors.GREEN}@EyeGodBot{Colors.RESET} - Поиск паролей и утечек
{Colors.GREEN}@QuickOSINT_bot{Colors.RESET} - OSINT: телефон, email, ник, IP
{Colors.GREEN}@LeakCheckBot{Colors.RESET} - Проверка утечек
{Colors.GREEN}@PasswordSearchBot{Colors.RESET} - Поиск паролей
{Colors.GREEN}@Tpoisk_bot{Colors.RESET} - Поиск по Telegram
{Colors.GREEN}@bmi_novichok_bot{Colors.RESET} - Поиск по базам данных
{Colors.GREEN}@TgAnalyst_bot{Colors.RESET} - Анализ аккаунта
{Colors.GREEN}@GetContact_bot{Colors.RESET} - Поиск по телефону
{Colors.GREEN}@OSINT_maigret_bot{Colors.RESET} - Поиск по нику (500+ сайтов)

{Colors.BOLD}Поисковые каналы:{Colors.RESET}
@leaks_channel - утечки
@osint_ru - OSINT новости  
@search_engines - поисковые системы
@database_sale - базы данных

{Colors.BOLD}Ручной поиск:{Colors.RESET}
https://t.me/search?q=запрос - поиск по Telegram
https://telegra.ph/search?q=запрос - поиск по статьям
""")
    
    def save_report(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"osint_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("OSINT REPORT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            for key, value in self.results.items():
                f.write(f"\n{'=' * 50}\n")
                f.write(f"{key.upper()}\n")
                f.write(f"{'=' * 50}\n")
                
                if isinstance(value, dict):
                    f.write(json.dumps(value, indent=2, ensure_ascii=False, default=str))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, tuple):
                            f.write(f"\n{item[0]}:\n")
                            f.write(json.dumps(item[1], indent=2, ensure_ascii=False, default=str))
                        else:
                            f.write(json.dumps(item, indent=2, ensure_ascii=False, default=str))
        
        print(f"\n{Colors.GREEN}[+] Отчет сохранен: {filename}{Colors.RESET}")
        return filename


def show_menu():
    print(f"\n{Colors.BOLD}{'═' * 35}{Colors.RESET}")
    print(f"{Colors.BOLD}  ГЛАВНОЕ МЕНЮ{Colors.RESET}")
    print(f"{'═' * 35}")
    print(f"  {Colors.GREEN}1{Colors.RESET}. 📧 Глубокий поиск по Email")
    print(f"  {Colors.GREEN}2{Colors.RESET}. 📱 Поиск по телефону")
    print(f"  {Colors.GREEN}3{Colors.RESET}. 🤖 Telegram OSINT гайд")
    print(f"  {Colors.GREEN}4{Colors.RESET}. 🚀 Комбо (email + телефон)")
    print(f"  {Colors.GREEN}0{Colors.RESET}. Выход")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print(f"\n{Colors.BOLD}ГЛУБОКИЙ OSINT - поиск по всем доступным базам{Colors.RESET}\n")
    print(f"Источники:")
    print(f"  {Colors.RED}● Have I Been Pwned — официальные утечки")
    print(f"  {Colors.RED}● Dehashed — крупнейшая база")
    print(f"  {Colors.RED}● LeakCheck — поиск в утечках")
    print(f"  {Colors.RED}● Psbdmp — реальные пароли")
    print(f"  {Colors.GREEN}● Gravatar — профиль и соцсети")
    print(f"  {Colors.GREEN}● EmailRep — репутация email")
    print(f"  {Colors.GREEN}● GitHub — поиск в коде")
    print(f"  {Colors.GREEN}● Google Dorks — глубокий поиск")
    print(f"  {Colors.GREEN}● IntelX — даркнет поиск\n")
    
    while True:
        show_menu()
        choice = input(f"\n  {Colors.CYAN}Выбор →{Colors.RESET} ").strip()
        
        if choice == '0':
            break
        
        osint = DeepOSINT()
        
        if choice == '1':
            email = input(f"\n  📧 Email: ").strip()
            if email and '@' in email:
                osint.search_email(email)
                if osint.results:
                    save = input(f"\n{Colors.CYAN}Сохранить отчет? (y/n): {Colors.RESET}").strip().lower()
                    if save in ['y', 'yes', 'д', 'да']:
                        osint.save_report()
        
        elif choice == '2':
            phone = input(f"\n  📱 Телефон: ").strip()
            if phone:
                osint.search_phone(phone)
        
        elif choice == '3':
            osint.show_telegram_osint()
        
        elif choice == '4':
            print(f"\n{Colors.BOLD}🚀 КОМБО ПОИСК{Colors.RESET}")
            email = input(f"  📧 Email: ").strip()
            phone = input(f"  📱 Телефон: ").strip()
            
            if email:
                osint.search_email(email)
            if phone:
                osint.search_phone(phone)
            
            if osint.results:
                save = input(f"\n{Colors.CYAN}Сохранить? (y/n): {Colors.RESET}").strip().lower()
                if save in ['y', 'yes', 'д', 'да']:
                    osint.save_report()
        
        input(f"\n{Colors.CYAN}Enter для продолжения...{Colors.RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()

if __name__ == '__main__':
    main()