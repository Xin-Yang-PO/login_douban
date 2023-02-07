"""
login the douban and get key cookie, there are two choice to do it(session and selenium)：
session method: to login douban with no verify;
    1：session.get status;
    2：session.post login;
    3: declare and assign global variables.
selenium method: to login douban with slider verification;
    1: create and instantiate the driver;
    2: initiate a login request;
    3: get the slip distance;
    4: drag and verify;
    5: declare and assign global variables.
"""
import json
import random
import time
import requests
import re
import cv2
from fake_useragent import UserAgent
from seleniumwire import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from lxml import etree


class login_with_none(object):
    """
    login douban with no verify: First, I am going to tell Douban I am logging in. Next to logging in.
    """

    def __init__(self, username, password):
        """
        :param username: your username
        :param password: your password
        """
        self.stat_url = 'https://www.douban.com/stat.html'  # get
        self.login_url = 'https://accounts.douban.com/j/mobile/login/basic'  # post
        # fake user agent
        self.user_agent = UserAgent().random
        # requests session object
        self.session = requests.session()
        # data for the get method
        self.get_data = {'action': 'login_click',
                         'platform': 'douban',
                         'login_click_time': time.time() * 1000,  # time stamp
                         'callback': 'jsonp_2ewcv5qa7fjfwbd'}  # random return
        self.username = username
        self.password = password

    def login(self):
        """
        :return: [0]get message, [1]description, [2]success or failed
        """
        # set session headers
        self.session.headers = {'User-Agent': self.user_agent}
        # method of get
        self.session.get(url=self.stat_url, data=self.get_data)
        response_1 = self.session.post(url=self.login_url, data={'remember': 'true',  # or false
                                                                 'name': self.username,
                                                                 'password': self.password})
        # get description
        description = json.loads(response_1.text)['status']
        # print(response_1.text)
        # print(description)
        if 'failed' in description:
            message = json.loads(response_1.text)['message']
            print(f'\033[0;31m{message+", execute the next program."}\033[0m')
            print('--------------------------------------------------')
            return 'Failed to get cookie.', description, 'failed'
        else:
            globals()['Set-Cookie'] = json.loads(json.dumps(dict(response_1.headers)))['Set-Cookie']
            return 'Success to get cookie.', description, 'success'
            # login_witn_none().login()[0]['Set-Cookie'] is the coookie


class login_with_verify(object):
    """
    login douban with a slider verify, this is one more verification than the function login_with_none, there
    is no good idea to deal with the tcaptcha which use the session, so i decide to use the selenium to do it.
    """
    def __init__(self, username, password):
        """
        @param username: your username
        @param password: your password
        """
        self.username = username
        self.password = password
        self.user_agent = UserAgent().random
        self.login_url = 'https://accounts.douban.com/passport/login'
        # instantiate object
        options = webdriver.EdgeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")
        service = Service(executable_path='msedgedriver.exe') # you driver path
        self.driver = webdriver.Edge(service=service, options=options)

    # noinspection PyUnresolvedReferences
    def distance(self):
        """
        get the slip diantance
        @return:slip distance
        """
        time.sleep(5)
        # use xpath extract url
        element = etree.HTML(self.driver.page_source)
        style = element.xpath('//*[@id="slideBg"]/@style')
        url_ = re.findall('url[(]"(.*?)"[)]', style[0], re.S)[0]
        # splicing url
        url = 'https://t.captcha.qq.com' + url_
        # get verify photo url and save
        img = None
        while True:
            try:
                reaponse = requests.get(url=url, headers={'User-Agent': self.user_agent})
                img = reaponse.content
                break
            except Exception as ex:
                print(ex)
                continue
        with open('verify.jpg', 'wb') as f:
            f.write(img)
        # 0=cv2.IMREAD_GRAYSCALE, 1=cv2.IMREAD_COLOR, -1=cv2.IMREAD_UNCHANGED
        image = cv2.imread('verify.jpg', 0)
        # gaussianblur
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        # binarization
        canny = cv2.Canny(blurred, 200, 400)
        # contour detection
        # the function cv2.findContours will return four values: (x, y)top-left coordinate of the matrix
        #                                                        (w, h)the width and height of the matrix
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            # return four values of the cv2.findContours
            x, y, w, h = cv2.boundingRect(contour)
            # print(x, y, w, h)
            # judgment window and return a true diantance, only twelve arguments were given,
            # if a null value is returned, run it again.
            if (w, h) in ((77, 91), (78, 91), (91, 77), (91, 78), (78, 77), (78, 104),
                          (104, 78), (78, 78), (77, 77), (91, 91), (91, 79), (79, 79)):
                return x

    def drag(self):
        """
        use selenium.webdriver.ActionChains to simulated mouse slide
        """
        # calculate the correct sliding distance by proportion
        move = (self.distance() - 50) * 0.51 - 6.5 + random.uniform(0, 1)
        print('Sliding Distance:', move)
        print('--------------------------------------------------')
        # simulated slip
        actions = webdriver.ActionChains(self.driver)
        actions.click_and_hold(
            self.driver.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]')
        )
        actions.move_by_offset(move, 0).perform()
        time.sleep(random.uniform(0, 1))
        # release
        actions.release().perform()

    def run(self):
        """
        run the class
        """
        self.driver.get(url=self.login_url)
        # implicit wait, only need to set the global value once
        self.driver.implicitly_wait(5)
        # explicit wait:until(true is over), until_not(false is over)
        WebDriverWait(self.driver, 5, 0.5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@class="account-tab-account"]'))).click()
        self.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(self.username)
        self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(self.password)
        self.driver.find_element(By.XPATH, '//*[@class="account-form-field-submit "]/a').click()
        # switch to frame
        iframe = WebDriverWait(self.driver, 20, 0.5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="tcaptcha_iframe_dy"]')))
        self.driver.switch_to.frame(iframe)
        # use explicit wait to wait for the element to complete loading
        WebDriverWait(self.driver, 10, 0.5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="tcOperation"]/div[8]')))
        self.drag()
        WebDriverWait(self.driver, 10, 0.5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="db-global-nav"]')))
        cookies = self.driver.get_cookies()
        for i in cookies:
            if i['name'] == 'dbcl2':
                globals()['Set-Cookie'] = i['name'] + '=' + i['value']
                # print(i['value'])
                # print(i['name'] + '=' + i['value'])
        self.driver.quit()


# program run entry, where the program starts running
if __name__ == '__main__':
    out = login_with_none(username='username', password='password').login()
    # session login fails, execute the selenium method
    if out[2] == 'failed':
        while True:
            try:
                login_with_verify(username='username', password='password').run()
                print(f'\033[0;33m Cookie: \033[0m', globals()['Set-Cookie'])
                # get the key cookie, end loop
                break
            except Exception as e:
                print(e)
                print('--------------------------------------------------')
                # get key cookie failed, return to loop
                continue
    # after the login using the session method is successful, the selenium method is not executed
    if out[2] == 'success':
        print(f'\033[0;33m Cookie: \033[0m', globals()['Set-Cookie'])
        quit()
