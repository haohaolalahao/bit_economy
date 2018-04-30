import requests
from bs4 import BeautifulSoup

def get_answer(student_number, student_password):
    url = 'https://online.bit.edu.cn'
    s = requests.session()
    r = s.get(url)
    # print(r.status_code)

    soup = BeautifulSoup(r.text, 'html.parser')
    inp = soup.findAll(name='input')

    new_url = r.url

    headers = {
        'Host':'login.bit.edu.cn',
        'Connection': 'keep-alive',
        'Content-Length': '139',
        'Cache-Control': 'max-age=0',
        'Origin': 'https://login.bit.edu.cn',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Save-Data': 'on',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': new_url,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'}

    data = {
        'username': student_number,
        'password': student_password,
        'lt':inp[4]['value'],
        'execution': inp[5]['value'],
        '_eventId': inp[6]['value'],
        'rmShown': inp[7]['value'],
    }

    in_page = s.post(new_url, data=data, headers=headers, )
    # print(in_page.status_code)
    page = s.get(in_page.url)
    url = 'http://online.bit.edu.cn/moodle/'
    main_page = s.get(url)
    soup = BeautifulSoup(main_page.text, 'html.parser')
    my_class_economy_href = soup.find(id='frontpage-course-list').find(name='a')['href']
    # print(my_class_economy_href)
    economy_page = s.get(my_class_economy_href)
    economy_page_soup = BeautifulSoup(economy_page.text, 'html.parser')
    week_urls = economy_page_soup.find(id='region-main').findAll(name='a')
    week_urls[-8]
    week_href = []

    for url in week_urls[-8:]:
        week_href.append(url['href'])

    #for 循环 进入周页面->进入周测试->for 循环 进入测试回顾 ->提取答案
    main_i = 1
    for url in week_href[0:8]:
        page_one = s.get(url)
        page_one_soup = BeautifulSoup(page_one.text, 'html.parser')
        link = page_one_soup.find(id='section-{}'.format(main_i)).findAll(name='a')[-1]['href']
        review_page = s.get(link)
        review_page_soup = BeautifulSoup(review_page.text, 'html.parser')
        links_1 = review_page_soup.find(id='region-main').findAll(name='a')

        path = '/Users/Wanghao/Desktop/bit_online/economy_section_{}.txt'.format(main_i)
        load_txt = {}
        with open(path,'r',encoding='utf-8') as f:
            for line in f.readlines():
                load = line.strip('\n').split('!')
                load_txt[load[0]] = load[1]
            f.close()

        #提取答案
        text_answer = {}
        # 每一周2次回顾*10道
        # 1-> len(links_1)
        for i in range(0, len(links_1)):
            url = links_1[i]['href']
            last_page = s.get(url)
            last_page_soup = BeautifulSoup(last_page.text, 'html.parser')

            for i in range(1, 11):
                div_question = last_page_soup.find(id='q{}'.format(i))
                qtext = div_question.find('div',{'class':'qtext'}).string
                answers = div_question.find('div',{'class':'answer'}).findAll('div')
                for a in answers:
                    if len(a['class']) > 1 :
                        if a['class'][-1] == 'correct':
                            answer = a.find('label').string
                        else:
                            answer = 'incorrect'
                if answer != 'incorrect':
                    if qtext not in text_answer:
                        text_answer[qtext] = answer

        with open(path,'a',encoding='utf-8') as f:
            sum = 0
            for i in text_answer.keys():
                if i not in load_txt:
                    f.write(i+'!'+text_answer[i]+'\n')
                    sum = sum+1
            print('第{}周存储完成，已存储{}道，新增{}道，现有{}道。'.\
            format(main_i,len(load_txt)-2,sum,len(load_txt)-2+sum))
            f.close()
        main_i = main_i+1
