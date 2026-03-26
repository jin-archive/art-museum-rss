import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
import urllib3
import time

# SSL 인증서 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 정상 작동이 확인된 7개 미술관 목록
MUSEUM_SITES = [
    {"id": "busan_art", "name": "부산시립미술관", "url": "https://art.busan.go.kr/anucmt/list.nm", "selector": "td.title a"},
    {"id": "moca", "name": "부산현대미술관", "url": "https://www.busan.go.kr/moca/news01", "selector": "td.subject a, .board-list a"},
    {"id": "daegu", "name": "대구미술관", "url": "https://daeguartmuseum.or.kr/index.do?menu_id=00000791", "selector": "td.title a, .board_list a"},
    {"id": "daejeon", "name": "대전시립미술관", "url": "https://www.daejeon.go.kr/dma/DmaBoardList.do?usrMenuCd=0601000000&menuSeq=6098", "selector": "td.subject a"},
    {"id": "ulsan", "name": "울산시립미술관", "url": "https://www.ulsan.go.kr/s/uam/bbs/list.ulsan?bbsId=BBS_0000000000000188&mId=001007002001000000", "selector": "td.subject a, .board_list a"},
    {"id": "suwon", "name": "수원시립미술관", "url": "https://suma.suwon.go.kr/news/news_list.do", "selector": "td.title a, td.subject a"},
    {"id": "cheongju", "name": "청주시립미술관", "url": "https://cmoa.cheongju.go.kr/www/selectBbsNttList.do?bbsNo=5&key=72", "selector": "td.p-subject a, td.subject a"}
]

def generate_individual_rss():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    for site in MUSEUM_SITES:
        print(f"[{site['name']}] 크롤링 시도 중...")
        
        fg = FeedGenerator()
        fg.id(site['url'])
        fg.title(f"{site['name']} 공지사항")
        fg.link(href=site['url'], rel='alternate')
        fg.description(f"{site['name']}의 최신 소식을 알려주는 RSS 피드입니다.")
        fg.language('ko')

        try:
            res = requests.get(site['url'], headers=headers, verify=False, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            posts = soup.select(site['selector'])
            
            if not posts:
                posts = soup.select('table tbody tr a, .board_list tbody tr a, .bo_tit a')

            count = 0
            for post in posts:
                if count >= 5: # 최신 글 5개만 추출
                    break
                    
                title = ' '.join(post.text.strip().split())
                if not title:
                    continue
                    
                raw_link = post.get('href', '')
                
                if not raw_link or raw_link == "#" or "javascript:" in raw_link.lower():
                    full_link = site['url']
                else:
                    full_link = urljoin(site['url'], raw_link)

                fe = fg.add_entry()
                fe.id(full_link + f"#{count}")
                fe.title(title)
                fe.link(href=full_link)
                fe.description(f"{site['name']}에 새로운 게시물 '{title}'이(가) 등록되었습니다.")
                count += 1
                
            if count > 0:
                print(f"  ✅ {count}개 추출 성공")
            else:
                print(f"  ⚠️ 글을 찾지 못했습니다.")
            
        except Exception as e:
            print(f"  ❌ 크롤링 오류: {e}")
        
        filename = f"rss_{site['id']}.xml"
        fg.rss_file(filename)
        print(f"  💾 {filename} 저장 완료!\n")
        
        time.sleep(2)

if __name__ == "__main__":
    generate_individual_rss()
