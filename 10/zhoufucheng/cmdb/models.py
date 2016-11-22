#encoding: utf-8

import json
import datetime

import MySQLdb

import gconf
import dbutils

SQL_VALIDATE_LOGIN_COLUMNS = ('id', 'name')

SQL_VALIDATE_LOGIN = 'select id, name from user where name = %s and password = md5(%s)'
SQL_USER_SAVE = 'insert into user(name, age, password) values(%s, %s, md5(%s))'

SQL_USER_LIST_COLUMNS = ('id', 'name', 'age')
SQL_USER_LIST = 'select id, name, age from user'

SQL_USER_BY_ID_COLUMNS = ('id', 'name', 'age')
SQL_USER_BY_ID = 'select id, name, age from user where id=%s'

SQL_USER_MODIFY = 'update user set name=%s, age=%s where id=%s'

SQL_VALIDATE_USER_MODIFY = 'select id from user where id != %s and name = %s'

SQL_USER_DELETE = 'delete from user where id = %s'

SQL_MACHINE_ROOM_COLUMNS = ('id', 'name', 'addr', 'ip_ranges')
SQL_MACHINE_ROOM_LIST = 'select id, name, addr, ip_ranges from machine_room'

SQL_MACHINE_ROOM_SAVE = 'insert into machine_room(name, addr, ip_ranges) values(%s, %s, %s)'
SQL_MACHINE_ROOM_DELETE = 'delete from machine_room where id=%s'

SQL_ASSET_LIST_COLUMNS = 'id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_LIST = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2;'

SQL_ASSET_SAVE_COLUMNS = 'sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_SAVE = 'insert into asset({columns}) values({values})'.format(columns=','.join(SQL_ASSET_SAVE_COLUMNS), values=','.join(['%s'] * len(SQL_ASSET_SAVE_COLUMNS)))

SQL_ASSET_BY_ID = 'select id,sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status from asset where status!=2 and id=%s;'

SQL_ASSET_MODIFY_COLUMNS = 'sn,hostname,os,ip,machine_room_id,vendor,model,ram,cpu,disk,time_on_shelves,over_guaranteed_date,buiness,admin,status'.split(',')
SQL_ASSET_MODIFY = 'update asset set {values} where id=%s and status!=2'.format(values=','.join(['{column}=%s'.format(column=column) for column in SQL_ASSET_MODIFY_COLUMNS]))

SQL_ASSET_DELETE = 'update asset set status=2 where id=%s'

SQL_HOST_CREATE = 'insert into monitor_host(ip,cpu,mem,disk,m_time,r_time) values(%s,%s,%s,%s,%s,%s)'

def get_users():
    _, rt_list = dbutils.execute_sql(SQL_USER_LIST, (), True)
    return [dict(zip(SQL_USER_LIST_COLUMNS, line)) for line in rt_list]

def validate_login(username, password):
    _, rt_list = dbutils.execute_sql(SQL_VALIDATE_LOGIN, (username, password), True)
    return  dict(zip(SQL_VALIDATE_LOGIN_COLUMNS, rt_list[0])) if rt_list else None


def validate_user_save(username, password, age):
    if username.strip() == '':
        return False, 'username is empty'
    if len(username.strip()) > 25:
        return False, 'username len is not gt 25'
    if password.strip() == '':
        return False, 'password is empty'
    if len(password.strip()) < 6 or len(password.strip()) > 25:
        return False, 'password len is between 6 and 25'

    if not str(age).isdigit() or int(age) < 1 or int(age) > 100:
        return False, 'age is not a between 1 and 100 integer'

    return True, ''


def user_save(username, password, age):
    rt_cnt, _ = dbutils.execute_sql(SQL_USER_SAVE, (username.strip(), age.strip(), password.strip()), False)
    return rt_cnt != 0


def get_user_by_id(uid):
    _, rt_list = dbutils.execute_sql(SQL_USER_BY_ID, (uid, ), True)
    return dict(zip(SQL_USER_BY_ID_COLUMNS, rt_list[0])) if rt_list else None


def validate_user_modify(uid, username, age):
    if not get_user_by_id(uid):
        return False, 'user is not found'
    if username.strip() == '':
        return False, 'username is empty'
    if len(username.strip()) > 25:
        return False, 'username len is not gt 25'
    if not str(age).isdigit() or int(age) < 1 or int(age) > 100:
        return False, 'age is not a between 1 and 100 integer'

    rt_cnt, _ = dbutils.execute_sql(SQL_VALIDATE_USER_MODIFY, (uid, username.strip()), True)
    if rt_cnt != 0:
        return False, 'username is same to other'

    return True, ''


def user_modify(uid, username, age):
    dbutils.execute_sql(SQL_USER_MODIFY, (username.strip(), age.strip(), uid), False)
    return True


def user_delete(uid):
    dbutils.execute_sql(SQL_USER_DELETE, (uid,), False)
    return True

def validate_charge_password(uid, upassword, musername, mpassword):
    #检查管理员密码是否正确
    if not validate_login(musername, mpassword):
        return False, '管理员密码错误'

    #密码要求长度必须大于等于6
    if len(upassword) < 6:
        return False, u'密码必须大于等于6'

    return True, ''

def charge_password(uid, upassword):
    _sql = 'update user set password=md5(%s) where id=%s'
    _args = (upassword, uid)
    dbutils.execute_sql(_sql, _args, False)


def get_machine_rooms():
    rt_cnt, rt_list = dbutils.execute_sql(SQL_MACHINE_ROOM_LIST, (), True)
    return [dict(zip(SQL_MACHINE_ROOM_COLUMNS, rt)) for rt in rt_list]

def get_machine_rooms_index_by_id():
    rt_list = get_machine_rooms()
    rt_dict = {}
    for room in rt_list:
        rt_dict[room['id']] = room
    return rt_dict

def validate_machine_room_save(name, addr, ip_ranges):
    if name.strip() == '' or addr.strip() == '' or ip_ranges.strip() == '':
        return False, 'name, addr, ip_ranges is empty'
    return True, ''

def machine_room_save(name, addr, ip_ranges):
    dbutils.execute_sql(SQL_MACHINE_ROOM_SAVE, (name.strip(), addr,strip(), ip_ranges.strip()), False)
    return True

def machine_room_delete(mrid):
    dbutils.execute_sql(SQL_MACHINE_ROOM_DELETE, (mrid, ), False)
    return True

def get_topn(src, topn=10):
    stat_dict = {}
    fhandler = open(src, "rb")

    for line in fhandler:
        line_list = line.split()
        key = (line_list[0], line_list[6], line_list[8])
        stat_dict[key] = stat_dict.setdefault(key, 0) + 1

    fhandler.close()

    result = sorted(stat_dict.items(), key=lambda x:x[1])
    return result[:-topn - 1:-1]

def get_assets():
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ASSET_LIST, (), True)
    assets = []
    machine_rooms = get_machine_rooms_index_by_id()
    for rt in rt_list:
        asset = dict(zip(SQL_ASSET_LIST_COLUMNS, rt))
        for key in 'time_on_shelves,over_guaranteed_date'.split(','):
            if asset[key]:
                asset[key] = asset[key].strftime('%Y-%m-%d')
        asset['machine_room_name'] = machine_rooms.get(asset['machine_room_id'], {}).get('name', '')
        assets.append(asset)
    return assets

def validate_asset_save(req):
    return True, ''
    return False, 'sn not empty'

def asset_save(req):
    values = []
    for column in SQL_ASSET_SAVE_COLUMNS:
        values.append(req.get(column, ''))

    rt_cnt, _ = dbutils.execute_sql(SQL_ASSET_SAVE, values, False)
    return rt_cnt != 0

def get_asset_by_id(aid):
    rt_cnt, rt_list = dbutils.execute_sql(SQL_ASSET_BY_ID, (aid,), True)
    assets = []
    for rt in rt_list:
        asset = dict(zip(SQL_ASSET_LIST_COLUMNS, rt))
        for key in 'time_on_shelves,over_guaranteed_date'.split(','):
            if asset[key]:
                asset[key] = asset[key].strftime('%Y-%m-%d')
        assets.append(asset)
    return assets[0] if assets else {}

def validate_asset_modify(req):
    return True, ''

def asset_modify(req):
    values = []
    for column in SQL_ASSET_MODIFY_COLUMNS:
        values.append(req.get(column, ''))
    values.append(req.get('id', 0))
    print SQL_ASSET_MODIFY
    print values
    rt_cnt, _ = dbutils.execute_sql(SQL_ASSET_MODIFY, values, False)
    return True

def asset_delete(aid):
    dbutils.execute_sql(SQL_ASSET_DELETE, (aid, ), False)
    return True

def monitor_host_create(req):
    values = []
    for key in ['ip','cpu','mem','disk','m_time']:
        values.append(req.get(key,''))
    values.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    dbutils.execute_sql(SQL_HOST_CREATE,values,False)
    return True

def monitor_host_list(ip):
    start_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    sql = 'select m_time,cpu,mem,disk from monitor_host where ip=%s and r_time > %s order by m_time asc'
    rt_cnt, rt_list = dbutils.execute_sql(sql, (ip,start_time), True)
    categories_list = []
    cpu_list = []
    mem_list = []
    disk_list = []
    for line in rt_list:
        categories_list.append(line[0].strftime('%H:%M'))
        cpu_list.append(line[1])
        mem_list.append(line[2])
        disk_list.append(line[3])   
    return {
            'categories': categories_list,
            'series': [
         {
            'name': 'CPU',
            'data': cpu_list
          }, {
              'name': u'内存',
              'data': mem_list
          }, {
              'name': u'硬盘',
              'data': disk_list
          }]
               
        }

if __name__ == '__main__':
    for i in xrange(100):
        user_save('name-%s' % i, '123456', 29)
