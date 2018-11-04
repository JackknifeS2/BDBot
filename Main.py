import gspread
import discord
import configparser
import re
import datetime as dt
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ディスコードトークンを他のファイルから持ってくるための記述
config = configparser.ConfigParser()
config.read('setting.ini')
section = 'discordtoken'

# スプレッドシートのAPIで持ってくるための記述.またその準備
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('BDbot-1758dd011623.json', scope)
gc = gspread.authorize(credentials)
bdtest = gc.open('BDtest')
worksheet1 = bdtest.worksheet('sheet1')
worksheet2 = bdtest.worksheet('sheet2')

# 登録の時間確認のためのリスト
add_list = []

# ディスコードのイベント作成
client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    message_str = str(message.content)
    find_message = re.search('!\w{2,3}', message_str)

    if find_message is not None:
        cat_message = message_str[1:find_message.end()]
        print(cat_message)
        com_message = message_str[find_message.end() + 1:]
        print(com_message)
        ch_list = worksheet1.findall(cat_message)
        if len(ch_list) != 0 and com_message in 'down':
            ch_cell = ch_list[0]
            print(str(ch_cell.row) + ',' + str(ch_cell.col) + ',' + ch_cell.value)

            chd_name = str(message.channel)
            cell_list1 = worksheet1.findall(chd_name)
            cell_list2 = worksheet2.findall(chd_name)
            if len(cell_list1) != 0:
                cell = cell_list1[0]
                print(str(cell.row) + ',' + str(cell.col) + ',' + cell.value)
                worksheet1.update_cell(ch_cell.row, cell.col, datetime.now().strftime('%Y/%m/%d %H:%M'))
                add_list.append([1, ch_cell.row, cell.col, datetime.now()])
                await client.send_message(message.channel, datetime.now().strftime(
                    '%Y/%m/%d %H:%M') + 'に' + ch_cell.value + '-CHの対象が討伐登録されたよ')

            if len(cell_list2) != 0:
                cell = cell_list2[0]
                print(str(cell.row) + ',' + str(cell.col) + ',' + cell.value)
                worksheet2.update_cell(ch_cell.row, cell.col, datetime.now().strftime('%Y/%m/%d %H:%M'))
                add_list.append([2, ch_cell.row, cell.col, datetime.now()])
                await client.send_message(message.channel, datetime.now().strftime(
                    '%Y/%m/%d %H:%M') + 'に' + ch_cell.value + '-CHの対象が討伐登録されたよ')

        if len(ch_list) != 0 and com_message in 'del':
            ch_cell = ch_list[0]
            chd_name = str(message.channel)
            cell_list1 = worksheet1.findall(chd_name)
            cell_list2 = worksheet2.findall(chd_name)
            if len(cell_list1) != 0:
                cell = cell_list1[0]
                print(str(cell.row) + ',' + str(cell.col) + ',' + cell.value)
                worksheet1.update_cell(ch_cell.row, cell.col, '')
                await client.send_message(message.channel, cell.value + ',' + ch_cell.value + 'の情報が削除されたよ')
                for list_c in reversed(add_list):
                    if list_c[0] == 1 and list_c[1] == ch_cell.row and list_c[2] == cell.col:
                        add_list.remove(list_c)

            if len(cell_list2) != 0:
                cell = cell_list2[0]
                print(str(cell.row) + ',' + str(cell.col) + ',' + cell.value)
                worksheet2.update_cell(ch_cell.row, cell.col, '')
                await client.send_message(message.channel, cell.value + ',' + ch_cell.value + 'の情報が削除されたよ')
                for list_c in reversed(add_list):
                    if list_c[0] == 2 and list_c[1] == ch_cell.row and list_c[2] == cell.col:
                        add_list.remove(list_c)

        for list_c in add_list:
            print(list_c)
            if list_c[0] == 1:
                add_times = list_c[3]
                print(add_times)
                if (add_times + dt.timedelta(hours=12)) <= datetime.now():
                    add_list.remove(list_c)
                    worksheet1.update_cell(ch_cell.row, cell.col, '')
            if list_c[0] == 2:
                add_times = list_c[3]
                print(add_times)
                if (add_times + dt.timedelta(hours=12)) <= datetime.now():
                    add_list.remove(list_c)
                    worksheet2.update_cell(ch_cell.row, cell.col, '')

    print('------------------------------------------------------')


client.run(config.get(section, 'token'))
