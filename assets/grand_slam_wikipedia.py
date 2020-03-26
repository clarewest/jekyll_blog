from lxml import html
import requests
import numpy as np
import pandas as pd

def get_grand_slam_winners(url):
    ## get the wikipedia page
    page = requests.get(url)
    tree = html.fromstring(page.content)
    
    ## find the table of interest, the first table of class "wikitable sortable"
    table = tree.xpath('//table[@class="wikitable sortable"]')[0]
    ## get each of the rows: <tr> </tr>
    rows = table.xpath('tbody/tr')
    
    ## take the header names 
    cols = [ cell.text_content().strip() for cell in rows[0] ]

    ## Collect each year in a list of lists
    years = []
    for row in rows[1:]:
        fields = [ cell.text_content().strip() for cell in row]
        try: 
            ## limiting it to the Open Era
            if int(fields[0]) >= 1968:
                years.append(fields)
        except ValueError:
            ## Extra AO in Dec 1977 causes a problem 
            ## "Evonne Goolagong (6/7) (Dec)" 
            ## just ignore her
            pass

    ## make a dataframe
    df = pd.DataFrame(years, columns= cols)
    
    ### Clean up 
    ## Remove the (n/total) values after each name
    df = df.replace(r" \(.*\)","", regex=True)
    ## Remove the last Australian open of the Amateur era
    ## nb ignore capitalisation of Era
    df = df.replace(r".*Amateur .ra ends", np.nan, regex=True)
    df = df.replace(r"Open .ra begins  ", "", regex = True)
    
    return(df)

WTA_url = 'https://en.wikipedia.org/wiki/List_of_Grand_Slam_women%27s_singles_champions'
ATP_url = 'https://en.wikipedia.org/wiki/List_of_Grand_Slam_men%27s_singles_champions'

wta = get_grand_slam_winners(WTA_url)
atp = get_grand_slam_winners(ATP_url)


wta['tour'] = 'Womens'
atp['tour'] = 'Mens'

wta.append(atp).to_csv("slams.csv", index=False)
