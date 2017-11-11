from application import app, db
from application.models import Race, Trainer, Course, Horse, Horses_races, Jockey, Breeder, Owner
from bs4 import BeautifulSoup
import requests
import re
import math
import datetime
from time import sleep

def insertTrainer():
    trainer = Trainer(**{'trainer_name': '池江', 'training_center': TrainingCenter.miho})
    db.session.add(trainer)
    db.session.commit()

def deleteTrainer():
    trainer = Trainer.query.filter_by(training_center=TrainingCenter.miho).first()
    db.session.delete(trainer)
    db.session.commit()


# res = requests.post(url, {'start_year': '2016', 'start_mon': '1', 'end_year': '2016', 'end_mon': '2'})
# url = 'http://db.netkeiba.com/'
# res = requests.post(url, {'pid': 'race_list', 'list': '100', 'start_year': '2016', 'start_mon': '1', 'end_year': '2016', 'end_mon': '2', 'jyo[]': ['06'], 'page': '1'})
# soup = BeautifulSoup(res.content, 'html.parser')
# race_info = soup.find("table",{'class':'race_table_01'})
# print(race_info)

def getRacesfromSearchPage(search):
    '''検索条件からレース情報取得

    Keyword argument:
    search -- dict(検索条件)
    例: {'start_year': 2013, 'start_mon': 3, 'end_year': 2013, 'end_mon': 3, 'jyo[]': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']}
    参考: http://db.netkeiba.com/?pid=race_search_detail

    Return: int(検索結果レース総数)
    '''

    url = 'http://db.netkeiba.com/'
    search_query = {'pid': 'race_list'}
    search_query.update(search)
    res = requests.post(url, search_query)
    soup = BeautifulSoup(res.content, 'html.parser')
    pager = soup.find("div",{'class':'pager'})
    pager_text = pager.find(text=True)
    race_count = re.search(u'(\d{1,4})件中', pager_text).group(1)
    max_page = math.ceil(int(race_count) / 100)
    for page in range(1, max_page + 1):
        search_query.update({'page' : page, 'list': '100'})
        res = requests.post(url, search_query)
        soup = BeautifulSoup(res.content, 'html.parser')
        race_table = soup.find("table",{'class':'race_table_01'})
        rows = race_table.find_all('tr')
        for i, tr in enumerate(rows):
            if(i == 0):
                continue
            cols = tr.find_all('td')
            a = cols[4].find('a')
            race_path = a.get('href')
            scrapeRace(race_path)
            sleep(5)

    return race_count

def scrapeRace(race_path):
    '''レース情報取得しDBに保存

    Keyword argument:
    race_path -- str(レース詳細ページパス)

    Return: void
    '''

    print('\n--- START: {0} ---'.format(race_path))
    # Raceモデル初期化
    new_race = Race()

    race_id = race_path.split('/')[2]
    new_race.race_year = int(race_id[0:4])
    new_race.courses_id = int(race_id[4:6])
    new_race.courses_count = int(race_id[6:8])
    new_race.courses_count_day = int(race_id[8:10])
    new_race.day_race_number = int(race_id[10:12])

    # ページ取得
    url = 'http://db.netkeiba.com' + race_path
    res = requests.get(url)
    print('- [GET] {0} ({1})'.format(url, res))
    soup = BeautifulSoup(res.content, 'html.parser')

    # レース情報
    race_info = soup.find("div",{'class':'mainrace_data'})
    if race_info == None:
        print('--- ERROR: NO DATA ---')
        return

    print('# レース詳細')
    race_info_h1 = race_info.find('h1')
    race_name = race_info_h1.find(text=True)
    race_name_split = race_name.split('(')
    if len(race_name_split) > 1:
        last = race_name_split.pop()
        race_rank_text = last[:-1]
        print('- (グレード): {0}'.format(race_rank_text))
        race_name = '('.join(race_name_split)
    new_race.race_name = re.sub(u'第\d+回', '', race_name)
    print('- (レース名): {0}'.format(new_race.race_name))

    span = race_info.find('span')
    race_detail = span.find(text=True)
    race_details = race_detail.split('/')
    race_details = [elem.replace('\xa0', '') for elem in race_details]
    # (例) race_details = ['芝右 内2周3600m', '天候 : 曇', '芝 : 良', '発走 : 15:25']
    # print(race_details)
    race_track_distance = race_details[0]

    track_text = race_track_distance[0]
    print('- (トラック): {0}'.format(track_text))
    # トラック変換
    if track_text == '芝':
        new_race.track = 1
    elif track_text == 'ダ':
        new_race.track = 2
    elif track_text == '障':
        new_race.track = 3
        # TODO: 障害の場合、芝+ダートの場合あり
    # print('- (回): {0}'.format(race_detail_split[0][1]))
    # print(race_track_distance)
    new_race.distance = race_track_distance[-5:-1]
    print('- (距離): {0}'.format(new_race.distance))
    new_race.weather = race_details[1].split(' : ')[1]
    print('- (天候): {0}'.format(new_race.weather))
    track_condition_text = race_details[2].split(' : ')[1][0]
    print('- (馬場状態): {0}'.format(track_condition_text))
    # 馬場状態変換
    if track_condition_text == '良':
        new_race.track_condition = 1
    elif track_condition_text == '稍':
        new_race.track_condition = 2
    elif track_condition_text == '重':
        new_race.track_condition = 3
    elif track_condition_text == '不':
        new_race.track_condition = 4
    race_time_text = race_details[3].split(' : ')[1]
    print('- (発走): {0}'.format(race_time_text))

    smalltxt = race_info.find("p",{'class':'smalltxt'})
    race_sub_detail = smalltxt.find(text=True)

    # レースグレード変換
    try:
        race_rank_text
        if race_rank_text == 'G1':
            new_race.race_rank = 1
        elif race_rank_text == 'G2':
            new_race.race_rank = 2
        elif race_rank_text == 'G3':
            new_race.race_rank = 3
    except NameError:
        if re.search(u'オープン', race_sub_detail):
            new_race.race_rank = 4
        elif re.search(u'1600万下', race_sub_detail):
            new_race.race_rank = 5
        elif re.search(u'1000万下', race_sub_detail):
            new_race.race_rank = 6
        elif re.search(u'500万下', race_sub_detail):
            new_race.race_rank = 7
        elif re.search(u'未勝利', race_sub_detail):
            new_race.race_rank = 8
        elif re.search(u'新馬', race_sub_detail):
            new_race.race_rank = 9
        elif re.search(u'未出走', race_sub_detail):
            new_race.race_rank = 10

    # レース時間変換
    race_month = re.search(u'(\d{1,2})月', race_sub_detail).group(1)
    race_day = re.search(u'(\d{1,2})日', race_sub_detail).group(1)
    race_hour = race_time_text.split(':')[0]
    race_minute = race_time_text.split(':')[1]
    new_race.race_datetime = datetime.datetime(new_race.race_year, int(race_month), int(race_day), int(race_hour), int(race_minute))

    # ハンデ変換
    if re.search(u'ハンデ', race_sub_detail):
        new_race.rule_handicap = True
    else:
        new_race.rule_handicap = False

    # 性別制限変換
    if re.search(u'牝', race_sub_detail):
        new_race.rule_mare = True
    else:
        new_race.rule_mare = False

    # 年齢制限変換
    if re.search(u'4歳以上', race_sub_detail):
        new_race.rule_age = 4
    elif re.search(u'4歳', race_sub_detail):
        new_race.rule_age = 3
    elif re.search(u'3歳', race_sub_detail):
        new_race.rule_age = 2
    elif re.search(u'2歳', race_sub_detail):
        new_race.rule_age = 1

    # レース結果
    print('# レース結果')
    race_result = soup.find("table",{'class':'race_table_01'})
    rows = race_result.find_all('tr')
    for i, tr in enumerate(rows):
        if(i == 0):
            continue

        is_run = True
        new_horses_races = Horses_races()

        cols = tr.find_all('td')
        for ci, td in enumerate(cols):

            a = td.find('a')
            if(a):
                text = a.find(text=True)
            else:
                text = td.find(text=True)
            # print(text)
            if ci == 0:
                try:
                    new_horses_races.order = int(text)
                    print('## 着順: {0}着'.format(new_horses_races.order))
                except ValueError:
                    is_run = False
                    new_horses_races.order = 0
                    print('## 着順: 未出走')
            elif ci == 1:
                new_horses_races.frame = int(text)
                print('- (枠番): {0}枠'.format(new_horses_races.frame))
            elif ci == 2:
                new_horses_races.number = int(text)
                print('- (馬番): {0}番'.format(new_horses_races.number))
            elif ci == 3:
                horse_name = text
                print('- (馬名): {0}'.format(horse_name))
                horse_path = a.get('href')
                new_horses_races.horse = get_horse(horse_name, horse_path)
            elif ci == 5:
                new_horses_races.weight = float(text)
                print('- (斤量): {0}'.format(new_horses_races.weight))
            elif ci == 6:
                jockey_name = text
                print('- (騎手): {0}'.format(jockey_name))
                jockey_path = a.get('href')
                new_horses_races.jockey = get_jockey(jockey_name, jockey_path)
            elif ci == 7:
                if is_run == False:
                    break
                print('- (タイム): {0}'.format(text))
                finish_times_ms_msec = text.split('.')
                finish_times_msec = int(finish_times_ms_msec[1]) * 100
                finish_times_m_s = finish_times_ms_msec[0].split(':')
                if len(finish_times_m_s) == 1:
                    finish_times_minute = 0
                    finish_times_sec = int(finish_times_m_s[0])
                else:
                    finish_times_minute = int(finish_times_m_s[0])
                    finish_times_sec = int(finish_times_m_s[1])
                new_horses_races.finish_time = datetime.timedelta(minutes=finish_times_minute, seconds=finish_times_sec, milliseconds=finish_times_msec)
            elif ci == 8:
                print('- (着差): {0}'.format(text))
                new_horses_races.margin = text
            elif ci == 10:
                print('- (通過): {0}'.format(text))
                if text is None:
                    continue
                positions = text.split('-')
                positions = [int(p) for p in positions]
                new_horses_races.position = positions
            elif ci == 11:
                print('- (上り): {0}'.format(text))
                last_time_s_ms = text.split('.')
                last_time_sec = int(last_time_s_ms[0])
                last_time_msec = int(last_time_s_ms[1]) * 100
                new_horses_races.last_time = datetime.timedelta(seconds=last_time_sec, milliseconds=last_time_msec)
            elif ci == 12:
                print('- (オッズ): {0}'.format(text))
                new_horses_races.odds = float(text)
            elif ci == 13:
                print('- (人気): {0}'.format(text))
                new_horses_races.favorite = int(text)
            elif ci == 14:
                print('- (馬体重): {0}'.format(text))
                body_weight = int(text.split('(')[0])
                new_horses_races.body_weight = body_weight
            elif ci == 20:
                print('- (賞金): {0}'.format(text))
                if text is not None:
                    new_horses_races.prize = float(text.replace(',', ''))


        new_race.race_horses.append(new_horses_races)

    # print(new_race.race_horses)
    db.session.add(new_race)
    db.session.commit()

    return

def get_horse(horse_name, horse_path):
    '''Horse取得(存在しない場合は保存して取得)

    Keyword argument:
    horse_name -- 競走馬名
    horse_path -- 競走馬詳細ページパス

    Return: Horse
    '''

    horse = Horse.query.filter_by(horse_name=horse_name).first()
    if horse is not None:
        return horse

    new_horse = Horse()
    new_horse.horse_name = horse_name

    url = 'http://db.netkeiba.com' + horse_path
    res = requests.get(url)
    print('- [GET] {0} ({1})'.format(url, res))
    soup = BeautifulSoup(res.content, 'html.parser')
    head = soup.find("div",{'class':'db_head_name'})
    head_txt_01 = head.find('p',{'class':'txt_01'})
    horse_info = head_txt_01.find(text=True)
    horse_infos = horse_info.split()
    if len(horse_infos) == 1:
        # 馬情報がない場合、例外として保存して即終了(例: /horse/2011103931/)
        db.session.add(new_horse)
        db.session.commit()
        print('- [INSERTED]: {0}'.format(new_horse))
        return new_horse
    elif len(horse_infos) == 2:
        sex_age = horse_infos[0]
        new_horse.color = horse_infos[1]
    else:
        sex_age = horse_infos[1]
        new_horse.color = horse_infos[2]
    if re.search(u'牡', sex_age):
        new_horse.sex = 1
    elif re.search(u'牝', sex_age):
        new_horse.sex = 2
    elif re.search(u'セ', sex_age):
        new_horse.sex = 3
    table = soup.find("table",{'class':'db_prof_table'})
    rows = table.find_all('tr')
    row_num = 0
    for tr in rows:
        if row_num == 0:
            td_birth = tr.find('td')
            birth_text = td_birth.find(text=True)
            birth_year = re.search(u'(\d{4})年', birth_text).group(1)
            birth_month = re.search(u'(\d{1,2})月', birth_text).group(1)
            birth_day = re.search(u'(\d{1,2})日', birth_text).group(1)
            new_horse.birth = birth = datetime.date(int(birth_year), int(birth_month), int(birth_day))
        if row_num == 1:
            a_trainer_name = tr.find('a')
            trainer_name = a_trainer_name.find(text=True)
            trainer_path = a_trainer_name.get('href')
            new_horse.trainer = get_trainer(trainer_name, trainer_path)
        if row_num == 2:
            a_owner_name = tr.find('a')
            owner_name = a_owner_name.find(text=True)
            owner_path = a_owner_name.get('href')
            new_horse.owner = get_owner(owner_name, owner_path)
        if row_num == 3:
            # TODO: 募集情報の場合を考慮(例: メドウヒルズ)
            a_breeder_name = tr.find('a')
            if a_breeder_name is None:
                continue
            breeder_name = a_breeder_name.find(text=True)
            breeder_path = a_breeder_name.get('href')
            new_horse.breeder = get_breeder(breeder_name, breeder_path)
            break
        row_num += 1

    db.session.add(new_horse)
    db.session.commit()
    print('- [INSERTED]: {0}'.format(new_horse))

    return new_horse

def get_jockey(jockey_name, jockey_path):
    '''Jockey取得(存在しない場合は保存して取得)

    Keyword argument:
    jockey_name -- 騎手名
    jockey_path -- 騎手詳細ページパス

    Return: Jockey
    '''

    jockey = Jockey.query.filter_by(jockey_name=jockey_name).first()
    if jockey is not None:
        return jockey

    new_jockey = Jockey()
    new_jockey.jockey_name = jockey_name

    url = 'http://db.netkeiba.com' + jockey_path
    res = requests.get(url)
    print('- [GET] {0} ({1})'.format(url, res))
    soup = BeautifulSoup(res.content, 'html.parser')
    head = soup.find("div",{'class':'db_head_name'})
    head_txt_01 = head.find('p',{'class':'txt_01'})
    jockey_info = head_txt_01.find(text=True)
    jockey_infos = jockey_info.split()
    if re.search(u'美', jockey_infos[1]):
        new_jockey.training_center = 1
    if re.search(u'栗', jockey_infos[1]):
        new_jockey.training_center = 2

    db.session.add(new_jockey)
    db.session.commit()
    print('- [INSERTED]: {0}'.format(new_jockey))

    return new_jockey

def get_trainer(trainer_name, trainer_path):
    '''Trainer取得(存在しない場合は保存して取得)

    Keyword argument:
    trainer_name -- 調教師名
    trainer_path -- 調教師詳細ページパス

    Return: Trainer
    '''

    trainer = Trainer.query.filter_by(trainer_name=trainer_name).first()
    if trainer is not None:
        return trainer

    new_trainer = Trainer()
    new_trainer.trainer_name = trainer_name

    url = 'http://db.netkeiba.com' + trainer_path
    res = requests.get(url)
    print('- [GET] {0} ({1})'.format(url, res))
    soup = BeautifulSoup(res.content, 'html.parser')
    head = soup.find("div",{'class':'db_head_name'})

    # headがない場合return(例: http://db.netkeiba.com/trainer/a028c/)
    if head is None:
        return new_trainer

    head_txt_01 = head.find('p',{'class':'txt_01'})
    trainer_info = head_txt_01.find(text=True)
    trainer_infos = trainer_info.split()
    # TODO: trainer_infoをsplitするか確認
    if re.search(u'地方', trainer_info):
        new_trainer.training_center = 3
    elif re.search(u'美', trainer_infos[1]):
        new_trainer.training_center = 1
    elif re.search(u'栗', trainer_infos[1]):
        new_trainer.training_center = 2

    db.session.add(new_trainer)
    db.session.commit()
    print('- [INSERTED]: {0}'.format(new_trainer))

    return new_trainer

def get_owner(owner_name, owner_path):
    '''Owner取得(存在しない場合は保存して取得)

    Keyword argument:
    owner_name -- 馬主名
    owner_path -- 馬主詳細ページパス

    Return: Owner
    '''

    owner = Owner.query.filter_by(owner_name=owner_name).first()
    if owner is not None:
        return owner

    new_owner = Owner()

    new_owner.owner_name = owner_name

    db.session.add(new_owner)
    db.session.commit()
    print('- [INSERTED]: {0}'.format(new_owner))

    return new_owner

def get_breeder(breeder_name, breeder_path):
    '''Breeder取得(存在しない場合は保存して取得)

    Keyword argument:
    breeder_name -- 生産者名
    breeder_path -- 生産者詳細ページパス

    Return: Breeder
    '''

    breeder = Breeder.query.filter_by(breeder_name=breeder_name).first()
    if breeder is not None:
        return breeder

    new_breeder = Breeder()

    new_breeder.breeder_name = breeder_name

    db.session.add(new_breeder)
    db.session.commit()
    print('- [INSERTED]: {0}'.format(new_breeder))

    return new_breeder


# scrapeRace('/race/201407020604/')
# scrapeRace('/race/201709020611/')
# scrapeRace('/race/201701020601/')
# scrapeRace('/race/201405030108/')
# scrapeRace('/race/201708040610/')

# get_trainer('米川昇', '/trainer/05509/')

# get_horse('フェイムゲーム', '/horse/2010104296/')

# getRacesfromSearchPage({'start_year': 2014, 'start_mon': 3, 'end_year': 2014, 'end_mon': 5, 'jyo[]': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']})
