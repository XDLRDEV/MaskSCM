import sys
import copy
import time

sys.path.append('../python-sdk/')
from call_console import execute as run

cname = 'SupplyChain'
caddr = '0x84139e0d46160aa2dd2541f499049095596891c9'
call = 'call'
send = 'sendtx'


def timestamp_to_format(timestamp=None, formats='%Y-%m-%d %H:%M:%S'):
    if timestamp:
        time_tuple = time.localtime(timestamp)
        print('time_tuple:', time_tuple)
        res = time.strftime(formats, time_tuple)
    else:
        res = time.strftime(formats)
    return res


def __init():
    global u_list, place, node_list
    u_list = [[[], [], [], []], [[], []]]
    place = []
    node_list = list(run([call, cname, caddr, 'GetSupplierList'])[0])


def get_list():
    global u_list, place
    minn = 0
    maxx = 0
    maxp = 1
    plot = []
    track = []
    x = []
    y = []
    for l in place:
        if l < minn:
            minn = l
        if l > maxx:
            maxx = l
    for i in range(minn, maxx + 1):
        plot.append(0)
        track.append(0)
    for l in place:
        plot[l - minn] += 1
    for i in plot:
        if i > maxp:
            maxp = i
    for l in place:
        x.append(0.1 + (l - minn) * 0.15)
        y.append(0.9 - (maxp - plot[l - minn]) * 0.15 - track[l - minn] * 0.3)
        track[l - minn] += 1
    ul = copy.deepcopy(u_list)
    ul[0].append(x)
    ul[0].append(y)
    return ul


def add_node(data, level):
    global u_list, place
    place.append(level)
    for i in range(0, 4):
        u_list[0][i].append(data[i])


def add_link(data):
    global u_list
    for i in range(0, 2):
        u_list[1][i].append(data[i])


def make_list(pre_node, now_node, level):
    global node_list
    node_list.remove(now_node)
    supplier_name = run([call, cname, caddr, 'GetSupplierInfo', now_node])[0]
    supplier_stuck = len(run([call, cname, caddr, 'GetSupplierStuck', now_node])[0])
    supplier_balance = run([call, cname, caddr, 'GetSupplierBalance', now_node])[0]
    add_node([now_node, supplier_name, supplier_stuck, supplier_balance], level)
    links = run([call, cname, caddr, 'GetSupplierRelation', now_node])
    links_prior = list(links[0])
    links_next = list(links[1])
    if pre_node in links_prior:
        links_prior.remove(pre_node)
        add_link([pre_node, now_node])
    if pre_node in links_next:
        links_next.remove(pre_node)
        add_link([now_node, pre_node])
    for node in links_prior:
        if node in node_list:
            make_list(now_node, node, level - 1)
        else:
            add_link([node, now_node])
    for node in links_next:
        if node in node_list:
            make_list(now_node, node, level + 1)
        else:
            add_link([now_node, node])


def program():
    global node_list
    while node_list:
        make_list('0', node_list[0], 0)


def make_list_ex(pr_id, s_id, level, mode):
    global u_list, place
    stuck_info_buff = run([call, cname, caddr, 'GetStuckInfo', s_id])
    stuck_info = str(stuck_info_buff[0]) + stuck_info_buff[1]
    stuck_flew = run([call, cname, caddr, 'GetStuckFlew', s_id])
    if not mode:
        level = level - len(stuck_flew[1]) + 1
    buf = 0
    for trs_time in stuck_flew[1]:
        u_list[0][0].append(stuck_info)
        u_list[0][4].append(s_id + str(buf))
        if buf == 0:
            sp1 = run([call, cname, caddr, 'GetSupplierInfo', stuck_flew[0][0]])[0]
            u_list[0][1].append('制造')
            u_list[0][2].append(sp1)
        elif buf < len(stuck_flew[0]):
            sp1 = run([call, cname, caddr, 'GetSupplierInfo', stuck_flew[0][buf - 1]])[0]
            sp2 = run([call, cname, caddr, 'GetSupplierInfo', stuck_flew[0][buf]])[0]
            u_list[0][1].append('物流')
            u_list[0][2].append(sp1 + ' -> ' + sp2)
            add_link([s_id + str(buf - 1), s_id + str(buf)])
        else:
            sp1 = run([call, cname, caddr, 'GetSupplierInfo', stuck_flew[0][buf - 1]])[0]
            u_list[0][1].append('使用')
            u_list[0][2].append(sp1)
            add_link([s_id + str(buf - 1), s_id + str(buf)])
        u_list[0][3].append(timestamp_to_format(trs_time))
        place.append(level + buf)
        buf += 1
    make_info = run([call, cname, caddr, 'GetMakeInfo', s_id])
    print(make_info)
    left = level - 1
    right = level + buf
    for s_f in make_info[0]:
        if s_f != pr_id:
            newbf = make_list_ex(s_id, s_f, left, False)
            add_link([s_f + str(newbf - 1), s_id + '0'])
    if mode and make_info[1]:
        make_list_ex(s_id, make_info[1][0], right, True)
        print('=================' + make_info[1][0] + '=======================' + s_id + str(buf - 1))
        add_link([s_id + str(buf - 1), make_info[1][0] + '0'])
    return buf


def program_ex(s_id):
    global u_list
    u_list[0].append([])
    make_list_ex('0', s_id, 0, True)


def get_list_ex():
    global u_list, place
    minn = 0
    maxx = 0
    maxp = 1
    plot = []
    track = []
    x = []
    y = []
    for l in place:
        if l < minn:
            minn = l
        if l > maxx:
            maxx = l
    for i in range(minn, maxx + 1):
        plot.append(0)
        track.append(0)
    for l in place:
        plot[l - minn] += 1
    for i in plot:
        if i > maxp:
            maxp = i
    for l in place:
        x.append(0.1 + (l - minn) * 0.15)
        y.append(0.9 - (maxp - plot[l - minn]) * 0.15 - track[l - minn] * 0.3)
        track[l - minn] += 1
    ul = copy.deepcopy(u_list)
    ul[0].append(x)
    ul[0].append(y)
    return ul
