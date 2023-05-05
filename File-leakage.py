import argparse
import concurrent.futures
import logging
import requests
import shutil
import xlwt
from bs4 import BeautifulSoup
from tabulate import tabulate
from tqdm import tqdm
import colorama
colorama.init()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def detect_leak(url, path, page_title):
    try:
        
        html_page = requests.get(url).text
        soup = BeautifulSoup(html_page, "html.parser")
        
        page_title = soup.title.text
    except Exception as e:
        logging.error(f"{url} 访问失败: {str(e)}")
        return

    full_url = url + path
    
    try:
        r = requests.get(full_url, timeout=5)
        
        if r.status_code == 200:
            logging.info(f'{full_url} 成功 页面标题：{page_title}')
            
            return (url, path, r.status_code, page_title)
        else:
            pass
    except requests.exceptions.RequestException as e:
        if str(e) == f"403 Client Error: Forbidden for url: {full_url}":
            pass
        else:
            pass
        return
        
def main(url_path, dict_path, output_file):
    text = "欢迎使用文件泄露检测工具 -by: 老谢"
    terminal_width, _ = shutil.get_terminal_size()
    centered_text = text.center(terminal_width)
    print(colorama.Fore.GREEN + centered_text + colorama.Style.RESET_ALL)

    print(colorama.Fore.RED + "在使用本工具时，请确保遵守当地的法律法规以及网络完全法等相关规定。请注意，本工具的使用不应违反任何隐私权或其他法律规定，并且您应该对自己的行为负责。" + colorama.Style.RESET_ALL)
    
    password = input(colorama.Fore.YELLOW + "[1] Yes：[2] No: " + colorama.Style.RESET_ALL)
    
    if password != "1":
        print(colorama.Fore.RED + "江湖再见！程序退出" + colorama.Style.RESET_ALL)
    else:
        print(colorama.Fore.GREEN + "您表示同意，程序继续," + colorama.Style.RESET_ALL)
        
        with open(url_path,encoding='utf-8') as f:
            urls = [line.strip() for line in f]
        with open(dict_path,encoding='utf-8') as f:
            dictionary = [line.strip() for line in f]

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for url in urls:
                url = url.strip()
                for path in dictionary:
                    futures.append(executor.submit(detect_leak, url, path, None))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        print(tabulate(results, headers=["URL", "Path", "Status", "Title"]))

        if output_file:
            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet('Result')
            row = 1
            worksheet.write(0, 0, 'URL')
            worksheet.write(0, 1, 'Path')
            worksheet.write(0, 2, 'Status')
            worksheet.write(0, 3, 'Title')
            for url, path, status, title in results:
                worksheet.write(row, 0, url)
                worksheet.write(row, 1, path)
                worksheet.write(row, 2, status)
                worksheet.write(row, 3, title)
                row += 1

            workbook.save(output_file)
            logging.info(f'检测结果已保存到 {output_file}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文件泄露检测程序")
    parser.add_argument("-u", "--url", help="待检测的 URL 文本路径", required=True)
    parser.add_argument("-d", "--wordlist", help="文件字典路径", required=True)
    parser.add_argument("-o", "--output", help="输出文件路径，如果不填写则不输出", default=None)
    args = parser.parse_args()
    main(args.url, args.wordlist, args.output)
