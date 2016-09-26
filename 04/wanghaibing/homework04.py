#!/usr/bin/evn python
#encoding:utf-8

def sorts(log_file,dst_file,y=1,n=10):
   r_file=open(log_file,'rb')
   w_file=open(dst_file,'wb')
   r_dict={}
   tmplist=[]
   num=1
   for line in r_file:
       key=line.split()
       key=(key[0],key[8],key[10])
       r_dict[key]=r_dict.setdefault(key,0)+1
   for k,v in r_dict.items():
       tmplist.append((k,v))

   tmplist=sorted(tmplist,key=lambda x:x[1],reverse=y)
   for i in tmplist:
        if num <= n:
           w_file.write('%s %s\n' %(i[1],i[0]))
           num += 1
   r_file.close()
   w_file.close()
   return 'OK,Please check file: %s' %dst_file
if __name__=='__main__':
   #arg1:处理日志文件函数;arg2:处理后的文件;arg3:0、False,按访问量升序排序,1、True按降序排序;agr4:名次数量
    sorts('www_access_20140823.log','logsort.txt',1,10)
    print  open('logsort.txt','r').read()
