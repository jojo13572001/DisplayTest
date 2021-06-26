import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

remoteUID = "831582076"
remoteOTP = "0000"
waitTime = 5

def init(screenID):
    options = Options()
    options.set_capability("acceptInsecureCerts", True)
    options.add_argument("--window-size=1920,882")
    options.add_argument('--allow-insecure-localhost')
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--auto-select-desktop-capture-source=" + screenID)
    return options

def launch(path, screenID):
    driver = webdriver.Chrome(options=init(screenID))
    driver.get(path)
    return driver

##-----deliver socket id to remote Display----------
def waitDisplayReady(driver):
    try:    
        print ("Start to wait for remote Display ready")
        uid = driver.find_element_by_id("uid")
        def ready(driver):
            if (uid.get_attribute("disabled")=='true'):
                return True
            return False
        element = WebDriverWait(driver, waitTime).until(ready)
        print ("Remote Display is ready")
        return True
    except:
        return False

##--------------login p2p server---------------------
def loginAndWaitReady(driver):
    print ("Start to login p2p server")
    login = driver.find_element_by_id('login')
    login.click()
    try:    
        print ("Start to wait for login success")
        def ready(driver):
            if (login.get_attribute("disabled")=='true'):
                return True
            return False
        element = WebDriverWait(driver, waitTime).until(ready)
        print ("Successfully login p2p server")
        return True
    except:
        return False

##---------Set remote id, otp and click share screen---
def startShare(driver):
    remoteUidText = driver.find_element_by_id('remote-uid')
    remoteUidText.send_keys(remoteUID)
    remoteUidButton = driver.find_element_by_id('set-remote-uid')
    remoteUidButton.click()
    otp = driver.find_element_by_id('otp')
    otp.send_keys(remoteOTP)
    share = driver.find_element_by_id('target-screen')
    share.click()

##---------wait until p2p stream is coming--------------
def waitStreamReady(driver):
    try:    
        print ("Start to wait for p2p stream ready")
        shareButtonId = driver.find_element_by_id('target-screen')
        def ready(driver):
            if (shareButtonId.get_attribute("disabled")=='true'):
                return True
            return False
        element = WebDriverWait(driver, waitTime).until(ready)
        print ("p2p stream is ready")
        return True
    except:
        return False

##---------Get stat report from text area----------------
def getStats(driver):
    print ("Start to get stat reports")
    statButtonId = driver.find_element_by_id('target-stats')
    dataTextId = driver.find_element_by_id('dataReceived')
    statButtonId.click()
    time.sleep(3)
    return dataTextId.get_attribute('value')