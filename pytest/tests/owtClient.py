import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

remoteUID = "831582076"
remoteOTP = "0000"

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
        element = WebDriverWait(driver, 5).until(ready)
    except:
        driver.quit()

##--------------login p2p server---------------------
def loginAndWaitReady(driver):
    print ("Start login p2p server")
    login = driver.find_element_by_id('login')
    login.click()
    loginId = driver.find_element_by_id("login")
    try:    
        print ("Start to wait for login success")
        def ready(driver):
            if (loginId.get_attribute("disabled")=='true'):
                return True
            return False
        element = WebDriverWait(driver, 5).until(ready)
    except: 
        print ('Login in p2p server fail')
        driver.quit()

##---------Set remote id, otp and click share screen---
def StartShare(driver):
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
        element = WebDriverWait(driver, 5).until(ready)
    except:
        driver.quit()

##---------Get stat report from text area----------------
def GetStats(driver):
    statButtonId = driver.find_element_by_id('target-stats')
    dataTextId = driver.find_element_by_id('dataReceived')
    statButtonId.click()
    return dataTextId.get_attribute('value')