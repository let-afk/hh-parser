import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import numpy as np

def hh_parser_to_csv():
    url = "https://hh.ru"
    vacancy = input("profession, position or company: ")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    params = {"page": 0}
    session = requests.Session()
    list_jobs = []
    while True:
        response = session.get(url + f"/search/vacancy?text={vacancy}", headers=headers, params=params)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("div", {"class": "serp-item"})
        for job in jobs:
            job_info = {"min_salary": np.NaN,
                        "max_salary": np.NaN,
                        "currency": None}
            title = job.find("a", {"class": "serp-item__title"})
            job_info["name_job"] = title.text
            job_info["link"] = title.get("href")
            salary = job.find("span", {"class": "bloko-header-section-2"})
            if salary:
                salary_info = salary.text.split()
                if salary_info:
                    if not salary_info[0].isdigit():
                        str_salary = ""
                        for ind in range(1, len(salary_info)):
                            if not salary_info[ind].isdigit():
                                break
                            else:
                                str_salary += salary_info[ind]
                        if salary_info[0] == "от":
                            job_info["min_salary"] = int(str_salary)
                        elif salary_info[0] == "до":
                            job_info["max_salary"] = int(str_salary)
                    else:
                        str_min_salary = ""
                        str_max_salary = ""
                        dash_index = 0
                        for ind in range(0, len(salary_info) - 1):
                            if not salary_info[ind].isdigit():
                                dash_index = ind
                                break
                            else:
                                str_min_salary += salary_info[ind]
                        job_info["min_salary"] = int(str_min_salary)
                        for ind in range(dash_index + 1, len(salary_info) - 1):
                            if not salary_info[ind].isdigit():
                                break
                            else:
                                str_max_salary += salary_info[ind]
                        job_info["max_salary"] = int(str_max_salary)
                    job_info["currency"] = salary_info[-1]
            list_jobs.append(job_info.copy())
        print(params["page"])
        params["page"] += 1
    df_jobs = pd.DataFrame(list_jobs)
    df_jobs.to_csv("jobs.csv")

hh_parser_to_csv()
