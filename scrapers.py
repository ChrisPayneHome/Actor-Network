import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# define function to retieve actors list
def retrievePage(url) :
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        name = soup.find("h3", {"itemprop":"name"}).text
        name = re.sub("\s\s+", " ", name).strip("\n")
        if re.search("[(\[][0-9]{4}[)\]]", name):
            print("Scraping cast list from: %s" % name)
            # check if there is a cast list for the url
            if str(soup.find("div", {"no_content":"list"})) != "None":
                raise Exception("No cast list for this film")
            else:
                html = soup.find('table', {"class":"cast_list"})
                cast_table = pd.read_html(str(html))
                cast_list = list(pd.DataFrame(cast_table[0]).iloc[:, 1])
            return(cast_list)
        else:
            print("Error: not a Movie")
    except Exception as e:
        print("Error: %s" % e)



# define function to update actor_table
def filterList(actor_list, actor_table):
    for actor in actor_list:
        for link in actor_list:
            # if actor and link are the same or invalid
            if actor in [np.nan, "nan", link, "Rest of cast listed alphabetically:"]:
                continue
            # ...else add the row to the table
            else:
                if link in [np.nan, "nan", "Rest of cast listed alphabetically:"]:
                    continue
                else:
                    new_row = [actor, link]
                    actor_table.loc[len(actor_table)] = new_row
    return(actor_table)



