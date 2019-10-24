# coding: utf-8

"""
The test will:
- Launch the Instagram app.
- Login to my account.
- Tap my timeline.
- Get insights (Impression) from each videos posted yesterday.

- Num of likes and views is gotten by Insta API(not graph API).
"""

import os
import unittest
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
import json, config, urllib3
from datetime import datetime
import time
import sys

counter = 0
views = 0
likes = 0

def get_media_recent(insta_iam):
    global counter
    targets = []
    target_counter = 0

    url = "https://api.instagram.com/v1/users/self/media/recent?access_token="+insta_iam
    now = datetime.now()

    try:
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        for c in json.loads(r.data)["data"]:
            if c["type"] == "video":
                i_time = datetime(*time.localtime(int(c["created_time"]))[:6])

                if i_time.year == now.year and i_time.month == now.month and i_time.day == now.day-1 and c["caption"]["text"].find("A search word") != -1:
                    global views
                    global likes
                    views += c["video_views"]
                    likes += c["likes"]["count"]
                    print("link: ", c["link"], "video_view: ", c["video_views"], "likes: ", c["likes"]["count"])
                    targets.append(target_counter)
            target_counter += 1

        print("Views: ", views, "Likes: ", likes)
        print(targets)
    except Exception as e: # not 200
        print(e)
        counter += 1
        if counter < 4:
            get_media_recent(insta_iam)

    return targets

def init():
    AT = config.IG_ACCESS_TOKEN
    return AT

class GetInsightsTests(unittest.TestCase):
    "Class to run tests for the Instagram."
    def setUp(self):
        desired_caps = {}
        desired_caps['automationName'] = 'UiAutomator2'
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '6.0'
        desired_caps['deviceName'] = 'Xperia Z5'
        desired_caps['appPackage']='com.instagram.android'
        desired_caps['appActivity']='com.instagram.android.activity.MainTabActivity'
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    def tearDown(self):
        "A final process."
        self.driver.quit()

    def test_single_player_mode(self):
        "A main process."
        sleep(3)
        element = self.driver.find_element_by_id("com.instagram.android:id/log_in_button")
        element.click()
        sleep(1)

        element = self.driver.find_element_by_id("com.instagram.android:id/login_username")
        element.send_keys(config.IG_ID)
        sleep(1)
        element = self.driver.find_element_by_id("com.instagram.android:id/password")
        element.send_keys(config.IG_PW)
        sleep(1)

        element = self.driver.find_element_by_id("com.instagram.android:id/next_button")
        element.click()
        sleep(5)

        # Move to a profile page.
        element = self.driver.find_element_by_xpath('//android.widget.FrameLayout[@content-desc=\"プロフィール\"]')
        element.click()
        sleep(2)

        # Change to a list view mode.
        element = self.driver.find_element_by_xpath('//android.widget.ImageView[@content-desc=\"リストビュー\"]')
        element.click()
        sleep(2)

        # Get a list of targets. 
        targets_list = get_media_recent(init())

        def get_impression(target_counter, total_imp):
            # Scroll a page.
            actions = TouchAction(self.driver)
            actions.press(x=500,y=1500).wait(3000).move_to(x=500, y=50).release().perform()
            sleep(3)

            # Tap a insight link.
            element = self.driver.find_element_by_id("com.instagram.android:id/inline_insights")
            element.click()
            sleep(1)

            # Search an "impression."
            actions.press(x=500,y=1500).wait(3000).move_to(x=500,y=50).release().perform()
            actions.press(x=500,y=1500).wait(3000).move_to(x=500,y=50).release().perform()
            sleep(1)


            # Get an impression num.
            try:
                element = self.driver.find_elements_by_class_name("android.widget.TextView")
                imp = 0

                for i in range(len(element)):
                    if element[i].text.find("インプレッション数") != -1:
                        imp = int(element[i+1].text.replace(",",""))
                        break
            except:
                pass

            if target_counter in targets_list:
                print(">>>>>>>>>>>>>>>>>> ", imp)
                total_imp += imp
                targets_list.remove(target_counter)
            if len(targets_list) == 0:
                print("Total impression: ", total_imp)
                sys.exit()


            self.driver.back()

            element = self.driver.find_element_by_xpath('//android.widget.ImageView[@content-desc=\"グリッドビュー\"]')
            element.click()
            element = self.driver.find_element_by_xpath('//android.widget.ImageView[@content-desc=\"リストビュー\"]')
            element.click()

            target_counter += 1
            return target_counter, total_imp

        target_counter = 0
        total_imp = 0
        for i in range(15):
            target_counter, total_imp = get_impression(target_counter, total_imp)
        print("Total impression: ", total_imp)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(GetInsightsTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
