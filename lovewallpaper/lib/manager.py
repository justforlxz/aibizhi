# -*- coding: utf-8 -*-
import ConfigParser
import urllib2
import os
import sys
import commands
from lib.VERSION import __VERSION__
try:
    import pynotify
except:
    print "No model"

#管理设置壁纸，下载壁纸
class Manager:

    """docstring for Manager"""
    def __init__(self):
        try:
            pynotify.init("LoveWallpaperHD")
        except:
            print "model"
        #初始化读取    
        self._cf = ConfigParser.ConfigParser()
        self.usr_home = os.path.expanduser('~') + "/.config/lovewallpaper"
        self._cf.read("%s/config"%(self.usr_home))
        #获取下载路径
        self.download_path = self._cf.get("Path", "Download") 
        try:
            self.palform =  self._cf.get("Config", "platform") 
        except:
            self.palform =  self._cf.set('Config', 'platform', '')
            self._cf.write(open("%s/config" % (self.usr_home), "w"))
        
        if not self.palform:
            self.palform = self.getPlatform()
            self.loadPlugin(self.palform)

    def getPlatform(self):
    
      #判断MacOS
      if sys.platform in ('mac', 'darwin'):
        return "Mac"
      #判断桌面环境
      if not self.get_output("plasma-desktop"):
          return "KDE"
      if not self.get_output("gnome-panel") and os.environ.get("DESKTOP_SESSION") == "gnome":
          return "Gnome"
      if not self.get_output("xfce4-panel"):
          return "XFCE"
      if not self.get_output("mate-panel"):
          return "MATE"
      if not self.get_output("lxpanel"):
          return "LXDE"
      
      return "GnomeShell"
     
    def get_output(self, cmd):
      status, output = commands.getstatusoutput("ps -A | grep %s" %cmd)
      return status


    def loadPlugin(self, platform):
      print "桌面环境：%s" %platform

      if platform == "KDE":
          from Plugin.KDE import WallpaperSetter, AutoSlide
      elif platform == "GnomeShell":
          from Plugin.GnomeShell import WallpaperSetter, AutoSlide
      elif platform == "XFCE":
          from Plugin.Xfce import WallpaperSetter, AutoSlide
      elif platform == "Mac":
          from Plugin.Mac import WallpaperSetter, AutoSlide
      elif platform == "Gnome":
          from Plugin.Gnome import WallpaperSetter, AutoSlide
      elif platform == "MATE":
          from Plugin.Mate import WallpaperSetter, AutoSlide
      elif platform == "LXDE":
          from Plugin.LXDE import WallpaperSetter, AutoSlide
      else:
          try:
                  if os.environ['KDE_FULL_SESSION'] == 'true':
                      from Plugin.KDE import  WallpaperSetter, AutoSlide
          except Exception, e:
                      try:
                          if os.environ['XDG_CURRENT_DESKTOP'] == 'XFCE':
                              from Plugin.Xfce import WallpaperSetter, AutoSlide
                          elif  os.environ['XDG_CURRENT_DESKTOP'] == 'Pantheon':
                              from Plugin.Gnome import WallpaperSetter, AutoSlide
                          else:
                              from Plugin.Gnome import WallpaperSetter, AutoSlide
                      except Exception, e:
                           from Plugin.Gnome import WallpaperSetter, AutoSlide
              # print self.download_path
      self.Setter = WallpaperSetter()
      self.AutoSlider = AutoSlide()

    def _reload(self):
        self.usr_home = os.path.expanduser('~') + "/.config/lovewallpaper"
        self._cf.read("%s/config"%(self.usr_home))
        self.download_path = self._cf.get("Path", "Download") 

        #判断下载目录是否存在
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        #重新判断所在平台
        self.palform = self.getPlatform()
        self.loadPlugin(self.palform)

    def download(self,key,url):
        """docstring for download"""
        # print url
        self._reload()
        try:
            # print self.download_path+key+".jpg"
            #创建下载
            f = open(self.download_path+key+".jpg",'wb')
            print "Begin download"
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'LovewallpaperLinux/'+__VERSION__)]
            response = opener.open(url)
            f.write(response.read())
            f.close()
            return True
        except Exception, e:
            #各种出错提示
            try:
                n = pynotify.Notification(" 爱壁纸HD", "网络出现错误，请检查后重试")
                n.show()
            except:
                print "No model"
            return False


    def setWallpaper(self, key, url):
            self._reload()
            try:
                if os.path.exists(self.download_path+key + ".jpg"):
                    self.Setter.setWallpaper(self.download_path, key)
                else:
                    self.download(key,url)
                    self.Setter.setWallpaper(self.download_path, key)
            except Exception, e:
                try:
                    n = pynotify.Notification("爱壁纸HD", "很抱歉因为不明原因，设置失败，请尝试手动设置")
                    n.show()
                except:
                    print "False"

            finally:
                return True

    def puresetWallpaper(self, url):
         self.Setter.puresetWallpaper(url)
         return True

    def prepareFiles(self):
        self._reload()
        self.format = ['jpg','jpeg','png','bmp']
        self.files = []
        print "path is " + self.download_path
        for p,d,f in os.walk(self.download_path):
            for myfile in f:
                if myfile.split(".")[-1].lower() in self.format:
                    self.files.append(os.path.join(p, myfile))
        print self.files
        return self.files
