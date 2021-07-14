from file_manipulation import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import os, glob, pyautogui, time, sys, pyperclip
from datetime import datetime
from typing import Any


def fix_Fit_Activity_Files():
    os.chdir(zwift_activity_dir)
    fitfile_list = glob.glob("*.fit")

    if not fitfile_list:
        sys.exit("Nothing to fix and upload to Strava.\nAborting...")
    else:
        print("Start fixing...\n")

        dir = os.path.dirname(__file__)
        WEB_DRIVER_PATH = os.path.abspath( os.path.join(dir, '..', 'webdriver', 'geckodriver.exe') )
        LOG_FILE_PATH = os.path.abspath( os.path.join(dir, '..', 'logfile', 'geckodriver.log') )
        driver = webdriver.Firefox(executable_path=WEB_DRIVER_PATH, service_log_path=LOG_FILE_PATH)
        driver.maximize_window()

        # Step 1: open the webpage of FIT File Tools
        driver.get("https://www.fitfiletools.com/#/top")

        for fitfile in fitfile_list:
            
            path_to_fitfile = os.path.join(zwift_activity_dir, fitfile)
            
            # check if the size of the fit file is larger than 10KB
            if (os.path.getsize(path_to_fitfile) < 10000):
                move_To_Original_Activities_Folder(fitfile)
            else:
                try:
                    print("Fixing " + fitfile + "...\n")

                    # Step 2: click the "Launch" button of "Time Adjuster"
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@href='#/adjuster']"))
                    )
                    element.click()

                    # Step 3: click the "... or select files" button
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@ng-file-select='']"))
                    )
                    element.click()
                    time.sleep(1)
                    
                    # Step 4: select the corresponding fit file to be fixed
                    pyperclip.copy(path_to_fitfile)   # copy to clipboard
                    pyautogui.hotkey('ctrl', "v")   # ctrl-v to paste from clipboard
                    finish_file_selection(element)
                    time.sleep(1)

                    # Step 5: select the start date of the activity
                    fit_filename = fitfile.split('-')

                    # convert a month number to a month name
                    fit_filename[1] = datetime.strptime(fit_filename[1], "%m").strftime("%B")

                    # convert time from 24-hour clock format to 12-hour clock format
                    hours = int(fit_filename[3])
                    if hours > 12:
                        afternoon = True
                        hours -= 12
                    else:
                        afternoon = False
                        if hours == 0:   # special case
                            hours = 12

                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@ng-model='dt']"))
                    )
                    element.clear()
                    dd_mm_yyyy = fit_filename[2] + '-' + fit_filename[1] + '-' + fit_filename[0]
                    element.send_keys(dd_mm_yyyy)
                    time.sleep(1)

                    # Step 6: select the start time (hours & minutes) of the activity
                    # fill in minutes
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@ng-model='minutes']"))
                    )
                    element.clear()
                    element.send_keys(fit_filename[4])
                    time.sleep(1)

                    # choose A.M. or P.M.
                    if not afternoon:
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//button[@ng-click='toggleMeridian()']"))
                        )
                        element.click()
                    
                    # fill in hours
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@ng-model='hours']"))
                    )
                    element.clear()
                    element.send_keys(str(hours))
                    time.sleep(1)

                    # Step 7: start fixing the activity file
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//a[@ng-click='adjust()']"))
                    )
                    element.click()

                    # Step 8: download your file
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, 'Click here to download your file!'))
                    )
                    element.click()
                    time.sleep(3)
                    pyautogui.press('return')
                    time.sleep(3)
                    
                    # Step 9: click the "Close" button of "Time Adjuster"
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, '« Close'))
                    )
                    element.click()

                    # Step 10: rename file in Downloads folder and move to FixedActivities folder
                    newfilename = fit_filename[1] + fit_filename[2] + '.fit'   # mmdd.fit
                    rename_FitFile(newfilename)
                    move_To_Fixed_Activities_Folder(newfilename)

                    # Step 11: move the original fit file in zwift_activity_dir to OriginalActivities folder
                    move_To_Original_Activities_Folder(fitfile)

                except TimeoutException:
                    print("ERROR - Timeout!")
                    driver.quit()

                except NoSuchElementException:
                    print("ERROR - Cannot find the element!")
                    driver.quit()
        
        # Step 12: finally, close the browser window
        driver.quit()
        print("---------- End of fixing ----------\n")


def finish_file_selection(element: Any):
    try:
        pyautogui.click()   # simulate a single, left-button mouse click at the mouse’s current position
    except:
        element.send_keys(Keys.RETURN)   # in case the mouse's click doesn't work... 
