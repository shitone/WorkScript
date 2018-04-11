#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ftplib import FTP
import os


class ProductFTP:
    def __init__(self, ip="10.116.32.113", port=21, user="xxzxftp", pwd="123456", timeout=5):
        self.ftp = FTP()
        self.ftp.set_pasv(True)
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.timeout = timeout

    def connect(self):
        try:
            self.ftp.connect(self.ip,self.port,self.timeout)
            self.ftp.login(self.user, self.pwd)
            return True
        except:
            return False

    def upload(self, upload_path, local_path, upload_file):
        local_file = os.path.join(local_path, upload_file)
        upload_path_list = str.split(upload_path, '/')
        for split_path in upload_path_list:
            try:
                self.ftp.cwd(split_path)
            except:
                try:
                    self.ftp.mkd(split_path)
                    self.ftp.cwd(split_path)
                except:
                    return False
        try:
            if not os.path.isfile(local_file):
                return False
            with open(local_file, "rb") as f:
                try:
                    self.ftp.delete(upload_file)
                except:
                    pass
                self.ftp.storbinary('STOR %s.tmp'%upload_file, f, 4096)
                self.ftp.rename(upload_file+'.tmp', upload_file)
                return True
        except:
            return False

    def dis_connect(self):
        try:
            self.ftp.quit()
        except:
            try:
                self.ftp.close()
            except:
                pass