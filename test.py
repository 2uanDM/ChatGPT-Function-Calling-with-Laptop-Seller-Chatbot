import json
import requests

from urllib.parse import quote


def build_params(from_pages: int):
    data = {
        "card_type": "story_news",
        "from": from_pages,
        "image_size_desktop": "300x225",
        "image_size_mobile": "253x190",
        "image_size_tablet": "174x130",
        "sections": "/policy",
        "size": 6
    }

    # Encode this data to query string in url
    return quote(json.dumps(data))


def fetch(from_page: int):
    url = f"https://www.coindesk.com/pf/api/v3/content/fetch/content-search?query={build_params(from_pages=from_page)}&d=323&_website=coindesk"

    payload = {}
    headers = {
        'authority': 'www.coindesk.com',
        'accept': '*/*',
        'accept-language': 'vi,en-US;q=0.9,en;q=0.8,vi-VN;q=0.7',
        'cookie': '_pbjs_userid_consent_data=3524755945110770; CookieConsent={stamp:%27knc1JSkCpupBARXIQIG6xbEQAWIvT8soL7X/i1XnxDfx3KgEf2d3nw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:8%2Cutc:1705239857756%2Cregion:%27vn%27}; _gcl_au=1.1.1777193036.1705239861; _rdt_uuid=1705239860950.28de24ce-46a1-45d3-b6ce-dae79b3114c3; _hjIncludedInSessionSample_1065293=1; _hjSessionUser_1065293=eyJpZCI6IjFkMmFlNzM0LWJkZDgtNTE2ZC1hZTJkLTdiMGExMTZlYWEwZiIsImNyZWF0ZWQiOjE3MDUyMzk4NjEyNDIsImV4aXN0aW5nIjp0cnVlfQ==; __qca=P0-1110916402-1705239861041; moe_uuid=5c3d1b3a-5f77-44c0-b1f3-7d5ff2ac85ee; USER_DATA=%7B%22attributes%22%3A%5B%5D%2C%22subscribedToOldSdk%22%3Afalse%2C%22deviceUuid%22%3A%225c3d1b3a-5f77-44c0-b1f3-7d5ff2ac85ee%22%2C%22deviceAdded%22%3Atrue%7D; _pubcid=ccd06fbc-417d-48f6-9339-c446f0724e23; _pubcid_cst=VyxHLMwsHQ%3D%3D; _fbp=fb.1.1705239878221.339969168; cookie=470da2f5-2877-4980-ba30-229c49f90717; cookie_cst=zix7LPQsHA%3D%3D; _au_1d=AU1D-0100-001705239880-5V7RWNSK-MXRS; _gid=GA1.2.1271296610.1705239881; AKA_A2=A; _parsely_session={%22sid%22:3%2C%22surl%22:%22https://www.coindesk.com/%22%2C%22sref%22:%22https://www.google.com/%22%2C%22sts%22:1705245814403%2C%22slts%22:1705242282405}; _parsely_visitor={%22id%22:%22pid=a8226ff3a949b4601842b27c5ac8f15c%22%2C%22session_count%22:3%2C%22last_session_ts%22:1705245814403}; _hjSession_1065293=eyJpZCI6ImNjMDg4Nzc1LTc2NjQtNGEzMS1hMTcwLTZlNDAzMDY1MWY2YSIsImMiOjE3MDUyNDU4MTQ4NzMsInMiOjEsInIiOjAsInNiIjoxfQ==; _hjAbsoluteSessionInProgress=1; __gads=ID=34ae9fb1d4a8bcaa:T=1705239776:RT=1705245812:S=ALNI_MbvqXr3p-v59-8E7zOyWYmbCKKyDA; sailthru_pageviews=3; RT="z=1&dm=www.coindesk.com&si=a3fa32e9-5a5f-4675-9b41-467e93cda377&ss=lrdnbuhi&sl=1&tt=3mq&rl=1&nu=3hv0s2v7&cl=wti"; sailthru_content=f4618b8837368562f9d01fbc250e974b98d1afe60707f2743cb71012751dc99a532800ca5c4e2b775da0078c587dc02e; sailthru_visitor=5e1c000b-e549-46cc-9f68-48e63cc69fd8; _awl=2.1705245853.5-09b443078f5d2ae797cb1ab8e29a7cf8-6763652d617369612d6561737431-0; _sp_ses.dcec=*; cto_bidid=G7z9ql91NjRPZERadUpUTWVNenQ3REVHU0VWNmpWMmV4am5LUUs5ciUyRm1EME9rNHVpSCUyQnhkVm9HYU5aNHhENlJ2cWhEMThLaXBWbkNOMm5hY0VGY3ZhZ2JCSUhCTExvVmVLWThHcnBTSWlFeDFiVmMlM0Q; _au_last_seen_pixels=eyJhcG4iOjE3MDUyMzk4ODAsInR0ZCI6MTcwNTIzOTg4MCwicHViIjoxNzA1MjM5ODgwLCJydWIiOjE3MDUyMzk4ODAsInRhcGFkIjoxNzA1MjM5ODgwLCJhZHgiOjE3MDUyMzk4ODAsImdvbyI6MTcwNTIzOTg4MCwidGFib29sYSI6MTcwNTIzOTg4MCwicHBudCI6MTcwNTIzOTg4MCwidW5ydWx5IjoxNzA1MjM5ODgwLCJzb24iOjE3MDUyNDU4NTksImFkbyI6MTcwNTI0NTg1OSwib3BlbngiOjE3MDUyNDU4NTksImltcHIiOjE3MDUyNDU4NTksImJlZXMiOjE3MDUyNDU4NTksImFtbyI6MTcwNTI0NTg1OSwiaW5kZXgiOjE3MDUyNDU4NTksImNvbG9zc3VzIjoxNzA1MjQ1ODU5LCJzbWFydCI6MTcwNTI0NTg1OX0%3D; _ga=GA1.2.1574069447.1705239778; cto_bundle=xpt5el9Ha3l1eFhzVGFlJTJCMlBFbzRwaTEyd2hBRnBBNUxqJTJGRHROeElTTWN3aUhjJTJGR0Q3amNDQkVUSGVZcmpSQ080MXgxbWwyR1BBNWNQbUlLWm9hQll3aU04bmJ0Z1dtUEUxM0RnSmxuNE9QNG4lMkZuTTBBOHUwYWwxanpqMUliVWlBSGpLQzhGc00lMkZhaUw5RjJKVU54NkFMa0ZOS2J1bDBITTgxc21QdFRaWXMxbjk2RGxTdHoxR0kyZHhNRjlBTkZ1bjJLJTJGTExrN29qSG9ZMVE1N1BCWHlYQ2xRJTNEJTNE; _ga_VM3STRYVN8=GS1.1.1705245814.2.1.1705245913.0.0.0; _sp_id.dcec=50a15c3326f10e35.1705239880.3.1705245919.1705240000',
        'referer': 'https://www.coindesk.com/policy/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)


if __name__ == "__main__":
    a = [x for x in range(0, 100, 12) if x % 12 == 0]

    output = []

    for i in a:
        results = fetch(from_page=i)
        elements = results["content_elements"]
        for x in elements:
            url = x["canonical_url"]
            url = f'https://www.coindesk.com/{url}'
            output.append(url)

    with open("output.json", "w") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
