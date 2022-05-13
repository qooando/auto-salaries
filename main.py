#!/usr/bin/env python3
import code
import logging
import time

logger = logging.getLogger("auto")
logging.basicConfig()

logger.setLevel(level=logging.DEBUG)
logger.info("Logger enabled")

from selenium.common.exceptions import InvalidSessionIdException, NoSuchElementException, TimeoutException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.support.wait import WebDriverWait
from config import *


@dataclass
class JobInfo:
    title: str
    meanSalary: float
    minSalary: float = None
    maxSalary: float = None


if __name__ == '__main__':
    logger.info("Start...")
    options = Options()
    profile = FirefoxProfile(profile_directory=profileDir)
    driver = webdriver.Firefox(firefox_profile=profile, options=options)

    try:
        driver.set_window_position(0, 0)
        driver.set_window_size(1024, 768)

        results = {}

        if os.path.isfile(outputOds):
            logger.info(f"Load {outputOds}")
            odsData = get_data(outputOds)
        else:
            logger.info(f"Create new {outputOds}")
            odsData = OrderedDict()
            odsData["Sheet 1"] = [
                ["Job", "Country", f"Mean Salary {myCurrency}"]
            ]

        sheetData = odsData["Sheet 1"]
        save_data(outputOds, odsData)

        combinations = []

        for job in jobs:
            for country in countries:
                combinations.append((job, country))

        driver.get(glassdoorUrl)

        def lazyRetrieve(locators):
                for locator in locators:
                    try:
                        # WebDriverWait(driver, 2).until(
                        #     presence_of_element_located(locator)
                        # )
                        return driver.find_element(*locator)
                    except TimeoutException:
                        continue
                    except NoSuchElementException:
                        continue
                raise NoSuchElementException(str(locators))

        def jobTitleElement():
                argsToTest=[
                    [By.ID, "sc.keyword"],
                    [By.ID, "KeywordSearch"],
                ]
                return lazyRetrieve(argsToTest)

        def jobLocationElement():
                argsToTest=[
                    [By.ID, "sc.location"],
                    [By.ID, "LocationSearch"],
                ]
                return lazyRetrieve(argsToTest)

        def jobSearchButton():
                argsToTest=[
                    [By.XPATH, "//button[@data-test = 'search-bar-submit']"],
                    [By.ID, "HeroSearchButton"],
                ]
                return lazyRetrieve(argsToTest)

        root = None

        for job, country in combinations:
            logger.debug(f"Search for {job} in {country}")
            try:
                driver.get(glassdoorUrl)
                # always start from the main page where seems to be
                # lesser controls

                # since the page seems to detach all elements after every operation
                # on input forms, just use lazy load of elements every time

                time.sleep(0.5)
                # avoid a fail on startup

                jobTitleElement().click()
                jobTitleElement().clear()
                jobTitleElement().send_keys(job)
                # time.sleep(0.5)

                jobLocationElement().click()
                jobLocationElement().clear()
                jobLocationElement().send_keys(country)
                time.sleep(0.5)
                # an antibot FORCES data in a cookie
                # and uses the cookie for the correct search
                # we need to wait for this operation before click

                jobSearchButton().click()
                # time.sleep(0.5)

                def waitCondition(root):
                    # if root:
                    #     return staleness_of(root)
                    # else:
                    return presence_of_element_located((By.ID, "nodeReplace"))

                WebDriverWait(driver, 100000).until(waitCondition(root))

                root = driver.find_element(By.ID, "nodeReplace")

                try:
                    noSalaryFound = root.find_element(By.XPATH, f".//[contains(text(),'Al momento non ci sono rapporti')]")
                except NoSuchElementException:
                    noSalaryFound = None

                if noSalaryFound:
                    logger.warning(f"> No salary element found for {job} in {country}")
                    continue

                meanSalaryElement = None
                meanSalary = None
                timeUnit = None
                salaryCurrency = None

                for currency in currencies:
                    meanSalaryElement = root.find_elements(By.XPATH, f".//span[contains(text(),'{currency}')]")
                    salaryCurrency = currency
                    if meanSalaryElement:
                        break

                if not meanSalaryElement:
                    logger.warning(f"> No salary element found for {job} in {country}")
                    continue

                meanSalaryElement = meanSalaryElement[0]

                meanSalary = meanSalaryElement.text.replace(".", "").replace(salaryCurrency, "").strip()

                if not meanSalary:
                    logger.warning(f"> Empty salary string for {job} in {country}")
                    continue

                # print("mean string:", meanSalary)
                if "/" in meanSalary:
                    logger.debug(f"> Salary and time unit merged, split them")
                    meanSalary, timeUnit = meanSalary.split("/")
                    meanSalary = meanSalary.strip()
                    timeUnit = meanSalary.strip()

                meanSalary = int(meanSalary)
                meanSalary = meanSalary * toYourCurrencyConversion[salaryCurrency]

                if not timeUnit:
                    timeUnit = meanSalaryElement.find_element(By.XPATH, f"../span[2]")
                    timeUnit = timeUnit.text.replace("/", "").strip().lower()

                if timeUnit in toYearConversion:
                    meanSalary = meanSalary * toYearConversion[timeUnit]
                else:
                    logger.debug(f"Unknown time unit: {timeUnit}")

                logger.info(f"> Mean salary {meanSalary} {myCurrency} for {job} in {country}")
                results[job] = JobInfo(title=job, meanSalary=meanSalary)

                sheetData.append([job, country, meanSalary])
                save_data(outputOds, odsData)

                # remove root from dom
                # thus we permit the script to securely load the next page
                driver.execute_script("return document.getElementById('nodeReplace').remove();")

            except InvalidSessionIdException as e:
                raise e
            except Exception as e:
                raise e

    finally:
        logger.info("Quit")

    driver.quit()

