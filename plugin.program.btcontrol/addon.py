import re
from time import sleep
from __builtin__ import True
import logging
import sys

import urllib
import urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from btdevices import btdevices

''' Filter for std error '''
class debugFilter(logging.Filter):
    def filter(self, record):
        if record.levelno < logging.INFO:
            return True
        else:
            return False

''' Create logger '''
logger = logging.getLogger("btctrl")
logger.setLevel(logging.DEBUG)

''' INFO level and above go to std out '''
hdlInfo = logging.StreamHandler(sys.stdout)
hdlInfo.setLevel(logging.CRITICAL)
logger.addHandler(hdlInfo)

''' DEBUG level go to std err '''
hdlDebug = logging.StreamHandler(sys.stderr)
hdlDebug.setLevel(logging.INFO)
f = debugFilter()
hdlDebug.addFilter(f)
logger.addHandler(hdlDebug)


def debugPrint(message, *args):
    xbmc.log(message, level=xbmc.LOGNOTICE)
    #logger.debug(message, *args)
    
def infoPrint(message, *args):
    xbmc.log(message, level=xbmc.LOGINFO)
    #logger.info(message, *args)
    
def errorPrint(message, *args):
    xbmc.log(message, level=xbmc.LOGERROR)
    #logger.error(message, *args)


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


if __name__ == '__main__':
    
    
    base_url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    args = urlparse.parse_qs(sys.argv[2][1:])
    
    mode = args.get('mode', None)
    addr = args.get('addr', None)
    desc = args.get('desc', None)
    
    debugPrint('baseurl: {}'.format(base_url))
    debugPrint('handle: {}'.format(addon_handle))
    debugPrint('args: {}'.format(args))


    addon = xbmcaddon.Addon()
    bt_path = addon.getSetting('bluetoothctl_path')
    
    debugPrint('bluetoothctl: {}'.format(bt_path))

    bt = btdevices(bt_path)

    if mode is None:
        bt.wait(1)
        bt.scan(True)
        bt.wait(10)
        bt.scan(False)
        bt.getPairedList()
        bt.getDeviceList()
        
        for device in bt.devices:
            url = build_url({'mode': 'info', 'desc': device['desc'], 'addr': device['addr']})
            li = xbmcgui.ListItem('{}'.format(device['desc']))
            li.addContextMenuItems([(addon.getLocalizedString(30020), 'RunPlugin({})'.format(build_url({'mode': 'pair', 'addr': device['addr']}))),
                                    (addon.getLocalizedString(30021), 'RunPlugin({})'.format(build_url({'mode': 'unpair', 'addr': device['addr']}))),
                                    (addon.getLocalizedString(30023), 'RunPlugin({})'.format(build_url({'mode': 'connect', 'addr': device['addr']}))),
                                    (addon.getLocalizedString(30024), 'RunPlugin({})'.format(build_url({'mode': 'disconnect', 'addr': device['addr']}))),
                                    (addon.getLocalizedString(30022), 'Container.Refresh')
                                    ],replaceItems=True)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,  listitem=li, isFolder=True)
    
        xbmcplugin.endOfDirectory(addon_handle)
        
        
    elif mode[0] == "unpair":
        bt.unpair(addr[0])
    elif mode[0] == "pair":
        bt.pair(addr[0])
    elif mode[0] == "connect":
        bt.connect(addr[0])
    elif mode[0] == "disconnect":
        bt.disconnect(addr[0])
    elif mode[0] == "info":
        devInfo = bt.info(addr[0])
        for key in devInfo:
            url = build_url({'mode': 'None'})
            li = xbmcgui.ListItem(key + ': {}'.format(devInfo[key]))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    
        xbmcplugin.endOfDirectory(addon_handle)
            
    bt.quit()
        
