from urllib.request import Request, urlopen
from json import loads
from time import sleep

with open('match_data.txt','w') as f:
    # general match information
    f.write('match_id')
    f.write(',win')
    f.write(',is_dire')
    f.write(',patch')
    f.write(',game_mode')
    f.write(',lobby_type')
    f.write(',duration')
    # in-game support stats
    f.write(',obs_placed')
    f.write(',sen_placed')
    f.write(',camps_stacked')
    # hero information
    f.write(',hero_id')
    f.write(',level')
    f.write(',item_0')
    f.write(',item_1')
    f.write(',item_2')
    f.write(',item_3')
    f.write(',item_4')
    f.write(',item_5')
    # economy stats
    f.write(',kda')
    f.write(',last_hits_per_min')
    f.write(',denies')
    f.write(',ka_per_min')
    f.write(',kills_per_min')
    f.write(',deaths_per_min')
    f.write(',gold_per_min')
    f.write(',xp_per_min')
    f.write(',pct_team_gpm')
    f.write(',pct_team_xpm')
    f.write('\n')
    
# Obtain a list of match summaries
    
req = Request('https://api.opendota.com/api/players/31631995/matches')

with urlopen(req) as response:
    match_summaries = loads(response.read())

counter = 0    

for summary in match_summaries:
    
    # query once per three seconds, AT MOST
    sleep(3)
    
    player_slot = summary['player_slot']
    dire = player_slot // 2 ** 7
    player_index = player_slot % 2 ** 7 + 5 * dire
    
    match_id = summary['match_id']
    
    if player_slot > 100 and summary['radiant_win']:
        win = 1
    elif player_slot < 100 and not summary['radiant_win']:
        win = 1
    else:
        win = 0
    
    game_mode = summary['game_mode']
    lobby_type = summary['lobby_type']
    duration = summary['duration']
    hero_id = summary['hero_id']

    game_minutes = duration / 60
    
    req = Request('https://api.opendota.com/api/matches/{}'.format(match_id))
    
    # with statement known to output
    # urllib.error.HTTPError: HTTP Error 502: Bad Gateway
    
    with urlopen(req) as response:
        match_data = loads(response.read())
    
    # obtain team stats
    
    team_gpm = 0
    team_xpm = 0
    
    if dire:
        team_range = range(5,10)
    else:
        team_range = range(1,5)
    
    for team_player in team_range:
        team_gpm += match_data['players'][team_player]['gold_per_min']
        team_xpm += match_data['players'][team_player]['xp_per_min']
    
    player_info = match_data['players'][player_index]
    
    patch = player_info['patch']
    
    # support information
    obs_placed = player_info['obs_placed']
    sen_placed = player_info['sen_placed']
    camps_stacked = player_info['camps_stacked']
    
    # hero information
    level = player_info['level']
    item_0 = player_info['item_0']
    item_1 = player_info['item_1']
    item_2 = player_info['item_2']
    item_3 = player_info['item_3']
    item_4 = player_info['item_4']
    item_5 = player_info['item_5']
    
    # economy and fighting
    kda = player_info['kda']
    lh_per_min = player_info['benchmarks']['last_hits_per_min']['raw']
    denies = player_info['denies']
    ka_per_min = (player_info['kills'] + player_info['assists']) / game_minutes
    deaths_per_min = player_info['deaths'] / game_minutes
    gpm = player_info['benchmarks']['gold_per_min']['raw']
    xpm = player_info['benchmarks']['xp_per_min']['raw']
    pct_team_gpm = gpm / team_gpm
    pct_team_xpm = xpm / team_xpm
    
    match_parameter_list = [match_id, win, dire, patch, game_mode, lobby_type, duration,
                            obs_placed, sen_placed, camps_stacked,
                            hero_id, level, item_0, item_1, item_2, item_3, item_4, item_5,
                            kda, lh_per_min, denies, ka_per_min, deaths_per_min, gpm, xpm, pct_team_gpm, pct_team_xpm]
    
    match_parameter_list = [str(x) for x in match_parameter_list]
    
    with open('match_data.txt','a') as f:
        f.write(','.join(match_parameter_list))
        f.write('\n')
        
    counter += 1
    
    if counter % 100 == 0:
        print('Matches obtained: {}/{}'.format(counter,len(match_summaries)))