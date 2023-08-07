import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
from matplotlib import pylab
import matplotlib.pyplot as plt
import networkx as nx


# define function to retieve actors
def retrieveCast(url) :
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            name = soup.find("h3", {"itemprop":"name"}).text
            name = re.sub("\s\s+", " ", name).strip("\n")
            print("Scraping cast list from: %s\n" % name)
                # check if there is a cast list for the url
            if str(soup.find("div", {"no_content":"list"})) != "None":
                raise Exception("No cast list for this film")
            elif str(soup.find('table', {"class":"cast_list"})) != "None":
                html = soup.find('table', {"class":"cast_list"})
                cast_table = pd.read_html(str(html))
                cast_list = list(pd.DataFrame(cast_table[0]).iloc[:, 1])
            else:
                print(soup.find('table', {"class":"cast_list"}))
            return(cast_list)
        else:
            print("Status code %i, can't connect to: %s\n" % (page.status_code, url))
            if page.status_code == 404:
                print("Can't retrieve page: status code %i\n" % page.status_code)
            else:
                print("Retrying")
                time.sleep(random.randint(1, 6))
                retrieveCast(url)
    except (KeyError, NameError, TypeError, AttributeError, IndexError) as e:
        print("Error: Can't retrieve cast list (%s)\n" % e)


# define function to update actor_table
def filterList(actor_list):
    add_rows = []
    try:
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
                        add_rows.append(pd.DataFrame({'Actor1':[actor], 'Actor2':[link]}))
        new_rows = pd.concat(add_rows)
        return(new_rows)
    except Exception as e:
        print("Error: Can't retrieve actor table (%s)" % e)


# define combined function to retrieve actors and table
def combinedRetrieve(url, dataframes):
    cast_list = retrieveCast(url)
    new_rows = filterList(cast_list)
    dataframes.append(new_rows)


# define function to retrieve sample urls with a number input
def getURLs():
    # define empty url list
    sample_urls = []
    # begin loop of range
    for i in range(1, 5000, 50):
        print("Scraping movies: %i - %i" % (i, i + 50))
        try:
            sample_url = "https://www.imdb.com/search/title/?title_type=feature&num_votes=25000,&view=simple&sort=user_rating,desc&start="+ str(i) +"&ref_=adv_nxt"
            page = requests.get(sample_url)
            soup = BeautifulSoup(page.content, "html.parser")
            movie_table = soup.findAll("div", {"class":"lister-item mode-simple"})
            # begin loop of movies within range
            for j in range(0, len(movie_table)):
                # find the 7 digit id number for each film entry
                movie_id = re.findall(r'[0-9]{7}', str(movie_table[j]))[0]
                movie_url = "https://www.imdb.com/title/tt" + movie_id + "/fullcredits?ref_=tt_cl_sm"
                sample_urls.append(movie_url)
        except Exception as e:
            break
    return(sample_urls)


# define function to create network image
def save_graph(graph,file_name):
    # initialze Figure
    plt.figure(num=None, figsize=(1000, 700), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_edges(graph, pos, edge_color = "white")
    nx.draw_networkx_labels(graph, pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name, bbox_inches="tight")
    pylab.close()
    del fig
