#/usr/bin/python3
# encoding: utf-8
'''
@author: Ezekeil
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: guo.zhijie@21vianet.com
@software: pycharm
@file: alert.py
@time: 2018/11/7 9:23
@desc:
'''

import paramiko
import time
import rrdtool
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import math

time1 = int(time.time())

time1_local = time.localtime(time1)
time1_beijing = time.strftime('%Y-%m-%d %H:%M:%S',time1_local)

print('当前时间: {}'.format(time1_beijing))

# rrds_info格式： ①rrd文件名,②设备名及端口,③备注信息,④in方向阈值(单位：M),⑤out方向阈值(单位：M)
rrds_info = [
    # ('x-dx8f-5800-cnc-b009-c_traffic_in_33228.rrd','<X-DX8F-5800-CNC-B009-C-VRF>T1/1/4','xx大兴-单联通','500','300'),
    # ('x-dx8f-5800-ct-c_traffic_in_23861.rrd','<X-DX8F-5800-CT-B010-C-VRF>T1/1/4','xx大兴-单联通','500','300'),
    # ('x-dx8f-5820-cnc-b009-vrf_traffic_in_34137.rrd','<X-DX8F-5820-CNC-B009-VRF>T1/0/1','xx大兴-单电信','500','150'),
    # ('x-dx8f-5820-ct-b010-vrf_traffic_in_34107.rrd','<X-DX8F-5820-CT-B010-VRF>T1/0/1','xx大兴-单电信','500','150'),
    # ('xb-dx-6f-5820-88-a-vrf_traffic_in_41348.rrd','<XB-DX-6F-5820-88-A-VRF>RAGG10','xx大兴-3B','400','100'),
    # ('xb-dx-6f-5820-88-b-vrf_traffic_in_41349.rrd','<XB-DX-6F-5820-88-B-VRF>RAGG10','xx大兴-3B','400','100'),
    # ('xb-m6-f4-5820-a-177-vrf_traffic_in_35417.rrd','<XB-M6-F4-5820-A-177-VRF>T1/0/1','xxM6-3B','300','100'),
    # ('xb-m6-f4-5820-b-178-vrf_traffic_in_35459.rrd','<XB-M6-F4-5820-B-178-VRF>T1/0/1','xxM6-3B','300','100'),
    # ('xb-m6-f4-5820-a-177-vrf_traffic_in_35418.rrd','<XB-M6-F4-5820-A-177-VRF>T1/0/2','xxM6-3B','200','100'),
    # ('xb-m6-f4-5820-b-178-vrf_traffic_in_35460.rrd','<XB-M6-F4-5820-B-178-VRF>T1/0/2','xxM6-3B','200','100'),
    ('x-dx8f-5800-cnc-b009-c_traffic_in_3012.rrd','<X-DX8F-5800-CNC-B009-C-VRF>T1/1/4','xx大兴-单联通','500','300'),
    ('x-dx8f-5800-ct-b010-c-vrf_traffic_in_13584.rrd','<X-DX8F-5800-CT-B010-C-VRF>T1/1/4','xx大兴-单联通','500','300'),
    ('x-dx8f-5820-cnc-b009-vrf_traffic_in_8846.rrd','<X-DX8F-5820-CNC-B009-VRF>T1/0/1','xx大兴-单电信','500','150'),
    ('x-dx8f-5820-ct-b010-vrf_traffic_in_8816.rrd','<X-DX8F-5820-CT-B010-VRF>T1/0/1','xx大兴-单电信','500','150'),
    ('xb-m6-f4-5820-a-177-vrf_traffic_in_9891.rrd','<XB-M6-F4-5820-A-177-VRF>T1/0/1','xxM6-3B','300','100'),
    ('xb-m6-f4-5820-b-178-vrf_traffic_in_9933.rrd','<XB-M6-F4-5820-B-178-VRF>T1/0/1','xxM6-3B','300','100'),
    ('xb-m6-f4-5820-a-177-vrf_traffic_in_9892.rrd','<XB-M6-F4-5820-A-177-VRF>T1/0/2','xxM6-3B','200','100'),
    ('xb-m6-f4-5820-b-178-vrf_traffic_in_9934.rrd','<XB-M6-F4-5820-B-178-VRF>T1/0/2','xxM6-3B','200','100'),
]

# rrds_agg_info格式： ①rrd-1文件名,②rrd-2文件名,③设备名及端口,④备注信息,⑤in方向阈值(单位：M),⑥out方向阈值(单位：M)
# 应对某些扫不出流量的合口，如agg口在cacti中显示流量，则添加到rrds——info中即可
rrds_agg_info = [
    ('xb-dx-6f-5820-88-a-vrf_traffic_in_11920.rrd','xb-dx-6f-5820-88-a-vrf_traffic_in_11921.rrd', '<XB-DX-6F-5820-88-A-VRF>RAGG10', '陌陌大兴-3B', '400', '100'),
    ('xb-dx-6f-5820-88-b-vrf_traffic_in_11924.rrd','xb-dx-6f-5820-88-b-vrf_traffic_in_11925.rrd', '<XB-DX-6F-5820-88-B-VRF>RAGG10', '陌陌大兴-3B', '400', '100'),
]


my_sender = ''  # 发件人邮箱账号
my_pass = ''  # 发件人邮箱密码
my_user1 = 'xx@21vianet.com'  # 收件人邮箱账号，我这边发送给自己
my_user2 = 'xx@21vianet.com'  # 收件人邮箱账号，我这边发送给自己
#my_user3 = 'xx@21vianet.com'  # 收件人邮箱账号，我这边发送给自己
#my_user4 = 'xx@21vianet.com'  # 收件人邮箱账号，我这边发送给自己

cmd_p1 = 'scp -l 30000 /database-a/rra/'
# cmd_p1 = 'scp /var/www/html/rra/'
cmd_p2 = ' root@xx.xx.xx.xx:/root'

def mail(content_info,titles):
    ret = True
    try:
        msg = MIMEText(content_info, 'plain', 'utf-8')
        msg['From'] = formataddr(["momo-alert", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr([" ", my_user1])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To'] = formataddr([" ", my_user2])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        # msg['To'] = formataddr([" ", my_user3])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        # msg['To'] = formataddr([" ", my_user4])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = titles  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP()
        server.connect("mail.xxx.com", 25)
        # smtp.set_debuglevel(1)
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user1,my_user2,], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret



#创建SSH对象
ssh = paramiko.SSHClient()
#把要连接的机器添加到known_hosts文件中
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='xx.xx.xx.13', port=, username='xx', password='xx')

cmd = '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n' \
      '{}{}{}\n'.format(cmd_p1,rrds_info[0][0],cmd_p2,
                        cmd_p1,rrds_info[1][0],cmd_p2,
                        cmd_p1,rrds_info[2][0],cmd_p2,
                        cmd_p1,rrds_info[3][0],cmd_p2,
                        cmd_p1,rrds_info[4][0],cmd_p2,
                        cmd_p1,rrds_info[5][0],cmd_p2,
                        cmd_p1,rrds_info[6][0],cmd_p2,
                        cmd_p1,rrds_info[7][0],cmd_p2,
                        cmd_p1,rrds_agg_info[0][0],cmd_p2,
                        cmd_p1,rrds_agg_info[0][1],cmd_p2,
                        cmd_p1,rrds_agg_info[1][0],cmd_p2,
                        cmd_p1,rrds_agg_info[1][1],cmd_p2,
                        )

stdin, stdout, stderr = ssh.exec_command(cmd)
result = stdout.read()
ssh.close()

time2 = int(time.time())
time3 = int(time.time() - 660)
time4 = time2 - 120
spend = time2 - time1

time2_local = time.localtime(time2)
time2_beijing = time.strftime('%Y-%m-%d %H:%M:%S',time2_local)
time3_local = time.localtime(time3)
time3_beijing = time.strftime('%Y-%m-%d %H:%M:%S',time3_local)

print('同步rrd总共花费{}s'.format(spend))
print('当前时间: {}'.format(time2_beijing))
print('开始循环')
for rrd in rrds_info:
    try:
        # print(rrd)
        # print('1打印rows')
        data=rrdtool.fetch(rrd[0],"AVERAGE",'--start={}'.format(time3),'--end={}'.format(time4))
        rows = data[2]
        # print('date:\n{}'.format(data))
        print('------------')
        # print('rows:\n{}'.format(rows))
        #最近的平均流量
        flow_in_now = (rows[4][0] + rows[5][0] + rows[6][0] + rows[7][0])/4
        flow_out_now = (rows[4][1] + rows[5][1] + rows[6][1] + rows[7][1])/4
        #print('flow_in_now:{}'.format(flow_in_now))
        #print('flow_out_now:{}'.format(flow_out_now))
        #稍远一些的平均流量
        flow_in_old = (rows[0][0] + rows[1][0] + rows[2][0] + rows[3][0]) / 4
        flow_out_old = (rows[0][1] + rows[1][1] + rows[2][1] + rows[3][1]) / 4
        #print('flow_in_old:{}'.format(flow_in_old))
        #print('flow_out_old:{}'.format(flow_out_old))
        #现有流量与5分钟前的差值
        flow_in_diff = int(flow_in_now - flow_in_old)
        flow_out_diff = int(flow_out_now - flow_out_old)
        #流量差值换算为M
        print_in = int(int(flow_in_diff)/1000/1000*8)
        print_out = int(int(flow_out_diff)/1000/1000*8)
        #阈值
        thold_in = int(rrd[3])
        thold_out = int(rrd[4])
        print('thold_in:{}M,thold_out:{}M'.format(thold_in,thold_out))
        print('flow_in_diff：{}M\nflow_out_diff:{}M'.format(print_in,print_out))
        if abs(print_in) > thold_in or abs(print_out) > thold_out:
            # rrds_info格式： ①rrd文件名,②设备名及端口,③备注信息,④in方向阈值(单位：M),⑤out方向阈值(单位：M)
            mail('    描述信息：{}\n'
                 '    告警内容：流量变化值traffic_in:{}M，traffic_out:{}M\n'
                 '    当前阈值：traffic_in:{}M，traffic_out:{}M\n'
                 '    设备端口：{}'.format(rrd[2],
                                      print_in,print_out,
                                      rrd[3],rrd[4],
                                      rrd[1]), 'xx-流量监控-报警（{}）'.format(rrd[2]))
            print('发送邮件告警')
        elif rows[7][0] == 0 or rows[7][1] == 0 or rows[6][0] == 0 or rows[6][1] == 0 or rows[5][0] == 0 or rows[5][1] == 0:
            mail('    描述信息：{}\n'
                 '    告警内容：近期内端口流量曾为空值\n'
                 '    当前阈值：traffic_in:{}M，traffic_out:{}M\n'
                 '    设备端口：{}'.format(rrd[2],
                                      rrd[3],rrd[4],
                                      rrd[1]), 'xx-流量监控-报警（{}）'.format(rrd[2]))
            print('发送邮件告警')
        else:
            print('{} ok'.format(rrd[1]))
    except Exception as e:
        print(e)


for rrd in rrds_agg_info:
    try:
        # print(rrd)
        # print('1打印rows')
        data1 =rrdtool.fetch(rrd[0],"AVERAGE",'--start={}'.format(time3),'--end={}'.format(time2))
        rows1 = data1[2]
        data2 =rrdtool.fetch(rrd[1],"AVERAGE",'--start={}'.format(time3),'--end={}'.format(time2))
        rows2 = data2[2]
        # print('date:\n{}'.format(data))
        print('------------')
        #最近的平均流量
        flow_in_now1 = (rows1[4][0] + rows1[5][0] + rows1[6][0] + rows1[7][0])/4
        flow_out_now1 = (rows1[4][1] + rows1[5][1] + rows1[6][1] + rows1[7][1])/4
        flow_in_now2 = (rows2[4][0] + rows2[5][0] + rows2[6][0] + rows2[7][0]) / 4
        flow_out_now2 = (rows2[4][1] + rows2[5][1] + rows2[6][1] + rows2[7][1]) / 4
        flow_in_now = flow_in_now1 + flow_in_now2
        flow_out_now = flow_out_now1 + flow_out_now2
        #print('flow_in_now:{}'.format(flow_in_now))
        #print('flow_out_now:{}'.format(flow_out_now))
        #稍远一些的平均流量
        flow_in_old1 = (rows1[0][0] + rows1[1][0] + rows1[2][0] + rows1[3][0]) / 4
        flow_out_old1 = (rows1[0][1] + rows1[1][1] + rows1[2][1] + rows1[3][1]) / 4
        flow_in_old2 = (rows2[0][0] + rows2[1][0] + rows2[2][0] + rows2[3][0]) / 4
        flow_out_old2 = (rows2[0][1] + rows2[1][1] + rows2[2][1] + rows2[3][1]) / 4
        flow_in_old = flow_in_old1 + flow_in_old2
        flow_out_old = flow_out_old1 + flow_out_old2
        #print('flow_in_old:{}'.format(flow_in_old))
        #print('flow_out_old:{}'.format(flow_out_old))
        #现有流量与5分钟前的差值
        flow_in_diff = int(flow_in_now - flow_in_old)
        flow_out_diff = int(flow_out_now - flow_out_old)
        #流量差值换算为M
        print_in = int(int(flow_in_diff)/1000/1000*8)
        print_out = int(int(flow_out_diff)/1000/1000*8)
        #阈值
        thold_in = int(rrd[4])
        thold_out = int(rrd[5])
        print('flow_in_diff：{}\nflow_out_diff:{}'.format(print_in,print_out))
        if abs(print_in) > thold_in or abs(print_out) > thold_out:
            # rrds_info格式： ①rrd文件名,②设备名及端口,③备注信息,④in方向阈值(单位：M),⑤out方向阈值(单位：M)
            mail('    描述信息：{}\n'
                 '    告警内容：流量变化值traffic_in:{}M，traffic_out:{}M\n'
                 '    当前阈值：traffic_in:{}M，traffic_out:{}M\n'
                 '    设备端口：{}'.format(rrd[2],
                                      print_in,print_out,
                                      rrd[3],rrd[4],
                                      rrd[1]), 'xx-流量监控-报警（{}）'.format(rrd[2]))
            print('发送邮件告警')
        elif rows1[7][0] + rows1[7][1] == 0 or rows2[7][0] + rows2[7][1] == 0 :
            mail('    描述信息：{}\n'
                 '    告警内容：近期内端口流量曾为空值\n'
                 '    当前阈值：traffic_in:{}M，traffic_out:{}M\n'
                 '    设备端口：{}'.format(rrd[2],
                                      rrd[3],rrd[4],
                                      rrd[1]), 'xx-流量监控-报警（{}）'.format(rrd[2]))
            print('发送邮件告警')
        else:
            print('{} ok'.format(rrd[2]))
    except Exception as e:
        print(e)




