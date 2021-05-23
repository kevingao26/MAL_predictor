# Run the below line from the command line
#pip install selenium

#---------------------------------------------
'''USER INPUT SECTION'''

# User's profile page
user_profile = 'electric_k9'

login = False # IF YOU WANT TO LOGIN (RECOMMENDED)
username = 'ENTER MAL USERNAME'
password = 'ENTERMAL PASSWORD'
#----------------------------------------------------


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import numpy as np
import time
import random

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
#options.add_argument('--headless') -- using headless mode currently leads to NoSuchElementException 
driver = webdriver.Chrome('./chromedriver', options=options)

# get a reference to the download menu. This will run before the page has 
# finished loading, so we stick it in a while loop and just keep looping
# until we're successful.
def find_by_id(element_id):
    while True:
        try:
            target = driver.find_element_by_id(element_id)
        except NoSuchElementException:
            time.sleep(0.2)
            continue
        else:
            break
    return target

def find_by_class(element_class):
    while True:
        try:
            target = driver.find_element_by_class_name(element_class)
        except NoSuchElementException:
            time.sleep(0.2)
            continue
        else:
            break
    return target


if login:
    driver.get("https://myanimelist.net/login.php?from=%2F")
    driver.implicitly_wait(5)
    driver.find_element_by_xpath("//*[@id='loginUserName']").send_keys(username)
    driver.find_element_by_xpath("//*[@id='login-password']").send_keys(password)
    driver.find_element_by_xpath("//*[@class='inputButton btn-form-submit btn-recaptcha-submit']").click()
    
    
user_link = "https://myanimelist.net/profile/" + user_profile
driver.get(user_link)
driver.get(user_link)
driver.implicitly_wait(3)

def page_scrape(df, link):
    
    
    malrow = {}
    
    ### MAIN PAGE ###

    
    #driver.get(link)  
    
    #0. Title
    wrapper_region = find_by_class("wrapper")
    title_region = wrapper_region.find_element_by_tag_name("h1")
    malrow["Title"] = title_region.text
    
    # Hyperlink

    malrow['Hyperlink'] = '=HYPERLINK("%s", "%s")' % (link.format(malrow["Title"]), malrow["Title"])

    # 1. Information Left Side
    wrapper_region = find_by_class("wrapper")
    content_region = wrapper_region.find_element_by_id("content")
    bord_region = content_region.find_element_by_class_name("borderClass")
    sty = bord_region.find_element_by_tag_name('div')
    rows = sty.find_elements_by_tag_name('div')

    def duration(st):
        minutes = 0
        if "sec" in st:
            minutes = int(st.split(" sec")[0]) / 60
            return minutes
        elif ("hr" in st) and ("min" in st):
            minutes = int(st.split(" hr")[0]) * 60
            rest = st.split(" hr")[1][2:]
            return int(rest.split(" min")[0]) + minutes
        elif "hr" in st:
            return int(st.split(" hr")[0]) * 60
        elif st == "Unknown":
            return None
        elif "min" in st:
            return int(st.split(" min")[0]) + minutes
    
    def raw2int(index, cutoff):
        if "A" in (rows[-(index)].text[cutoff:].replace(',', '')):
            return None
        return int(rows[-(index)].text[cutoff:].replace(',', ''))
    
    while (rows[-1].text[:10] != 'Favorites:'):
        rows.remove(rows[-1])

    malrow["Source"] = rows[-11].text[8:]
    malrow["Genres"] = rows[-10].text.split(": ")[1:][0].split(", ")
    malrow["Duration"] = duration(rows[-9].text[10:])
    
    if ("A" in rows[-7].text[7:]):
        malrow["ScoredCount"] = None
        malrow["Score"] = None
    else:
        malrow["ScoredCount"] = int(rows[-7].text[7:].split(" (")[1].split("by ")[1].split(" users")[0].replace(',', ''))
        malrow["Score"] = float(rows[-7].text[7:].split(" (")[0])
    
    malrow["Ranked"] = raw2int(5, 9)
    malrow["Popularity"] = raw2int(3, 13)
    malrow["Members"] = raw2int(2, 9)
    malrow["Favorites"] = raw2int(1, 10)
    
    # 2A. Information Right Side - Synopsis
    wrapper_region = find_by_class("wrapper")
    content_region = wrapper_region.find_element_by_id("content")
    bord_region = content_region.find_element_by_class_name("js-scrollfix-bottom-rel")
    synopsis_region = bord_region.find_element_by_tag_name('p')
    malrow["Synopsis"] = synopsis_region.text
    
    '''
    # 2B. Information Right Side - Staff
    big_region = bord_region.find_elements_by_class_name('pb24')[-1]
    char_region = big_region.find_elements_by_tag_name("div")[4]
    va_region = char_region.find_elements_by_class_name('borderClass')

    k = 0
    va_list = []
    for entry in va_region:
        if (k % 3 == 2):
            va_list.append(entry.text.split("\n")[0])
        k += 1

    malrow["Voice Actors"] = va_list
    '''
    
    ### STATS ###
    
    # 3. Stats
    time.sleep(np.random.rand() * 5)
    driver.get(link + "/stats")

    wrapper_region = find_by_class("wrapper")
    content_region = wrapper_region.find_element_by_id("content")
    bord_region = content_region.find_element_by_class_name("js-scrollfix-bottom-rel")
    stat_region = bord_region.find_elements_by_class_name('spaceit_pad')


    def stat2int(index, cutoff):
        return int(stat_region[index].text[cutoff:].replace(',', ''))

    def stat2score(index):
        return int(stat_region[index].text.replace('v', '(').split(' (')[1])

    malrow["Watching"] = stat2int(0, 9)
    malrow["Completed"] = stat2int(1, 11)
    malrow["On-Hold"] = stat2int(2, 9)
    malrow["Dropped"] = stat2int(3, 9)
    malrow["Plan to Watch"] = stat2int(4, 15)
    malrow["Total"] = stat2int(5, 7)
    
    if (len(stat_region) == 16):
        sum = 0
        for i in range(1, 11):
            malrow[str(i)] = stat2score(16 - i)
            sum += stat2score(16 - i)
        malrow["ScoredCount"] = sum
        for i in range(1, 11):
            malrow[str(i)] = malrow[str(i)] / sum * 100
    else:
        for i in range(1, 11):
            malrow[str(i)] = None
    

    # Final steps
    df = df.append(malrow, ignore_index=True)
    return df



all_df = pd.DataFrame()

for i in [1, 6, 2, 4]:
    status = i
    user_link = "https://myanimelist.net/animelist/" + user_profile + "?status=" + str(i) + "&tag="

    driver.get(user_link)

    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    mal_list = find_by_id('list-container')
    table = mal_list.find_element_by_tag_name('table')
    rows = table.find_elements_by_tag_name('tbody')
    #header_row = rows[0]
    rows_text = [row.text.split('\n') for row in rows[1:]]
    #df = pd.DataFrame(rows_text, columns = header_row.text.split('\n'))
    df = pd.DataFrame(rows_text, columns = [i for i in np.arange(1, 6)])
    
    df = df.drop([2], axis=1)
    df["Title"] = (df[1].str.split(None, 1).str[1])
    df = df.drop(1, axis=1)
    df["Score"] = (df[3].str.split(None, 1).str[0])
    df["Type"] = (df[3].str.split(None, 1).str[1])
    df = df.drop(3, axis=1)
    df["Rated"] = (df[5].str.split(None, 3).str[0])
    df["Aired Month"] = (df[5].str.split(None, 3).str[1])
    df["Aired Year"] = (df[5].str.split(None, 3).str[2])
    df["Studio"] = (df[5].str.split(None, 3).str[3])
    df = df.drop(5, axis=1)
    df = df.rename(columns={4: "Episodes"})
    df['Title'] = df['Title'].map(lambda x: x.replace(' Watch Episode Video', ''))
    
    if status != 2:
        ep_split = df["Episodes"].str.split(" / ")
        df["Episodes Watched"] = ep_split.str[0]
        df["Episodes"] = ep_split.str[1]
    else:
        df["Episodes Watched"] = df["Episodes"]
        
    
    if status == 1:
        df["Status"] = "Currently Watching"
    elif status == 2:
        df["Status"] = "Completed"
    elif status == 3:
        df["Status"] = "On-Hold"
    elif status == 4:
        df["Status"] = "Dropped"
    elif status == 6:
        df["Status"] = "Plan to Watch"
    else:
        print("Error in status #")
        
        
        
    #------------------------------------
    
    # 1-5 from this class are header titles. Start at index 5 (#6).
    all_shows = driver.find_elements_by_xpath("//*[@class='link sort']")[5:]
    stopper = 2


    ps_df = pd.DataFrame(columns=[
        "Title", "Hyperlink", "Episodes", "Date Started", "Date Finished", "Score", "Synopsis", "Source", "Genres", "Duration", 
        "Ranked", "Popularity", "Members", "Favorites",
        "Watching", "Completed", "On-Hold", "Dropped", "Plan to Watch", "Total", "1", "2", "3", "4", "5", "6", "7",
        "8", "9", "10", "ScoredCount"
    ])

    date_index = 0
    date_finished = []
    date_started = []
    for i in all_shows:
        if stopper == 0:
            break
        i.send_keys(Keys.CONTROL + Keys.ENTER)
        time.sleep(np.random.rand() * 5)
        assert len(driver.window_handles) > 1
        driver.switch_to.window(driver.window_handles[1])

        ps_df = page_scrape(ps_df, driver.current_url)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(np.random.rand() * 5)
        
        if login:
	        edit_region = driver.find_elements_by_xpath("//*[@class='List_LightBox']")[date_index]
	        edit_region.send_keys(Keys.CONTROL + Keys.ENTER)
	        time.sleep(np.random.rand() * 5)
	        driver.switch_to.window(driver.window_handles[1])

	        try:
	            history_region = driver.find_element_by_xpath("//*[@class='thickbox']")
	            history_region.send_keys(Keys.CONTROL + Keys.ENTER)
	            time.sleep(np.random.rand() * 4)
	            driver.switch_to.window(driver.window_handles[2])
	            time.sleep(np.random.rand() * 4 + 2) 

	            list_region = driver.find_elements_by_xpath("//*[@class='spaceit_pad']")
	            if (len(list_region) != 0):
	                date_finished.append(list_region[0].text[18:-7])
	                date_started.append(list_region[-1].text[18:-7])
	            else:
	                date_finished.append('')
	                date_started.append('')

	            driver.close()
	            driver.switch_to.window(driver.window_handles[1])
	            driver.close()
	            driver.switch_to.window(driver.window_handles[0])

	        except NoSuchElementException:
	            date_finished.append('')
	            date_started.append('')

	            
	            driver.close()
	            driver.switch_to.window(driver.window_handles[0])

	        time.sleep(np.random.rand() * 5)
	        date_index += 1
        
        #stopper -= 1

    ps_df = ps_df.drop("Episodes", axis=1)

    if login:
	    ps_df["Date Finished"] = date_finished
	    ps_df["Date Started"] = date_started
   
    #---------------------------------------
    
    final_df = pd.merge(df, ps_df, on="Title")
    final_df = final_df.rename(columns={"Score_x": "User Score", "Score_y": "MAL Score"})
    
    all_df = pd.concat([all_df, final_df])


driver.close()

#df['Genres'].fillna('NA', inplace = True)
flat_genre = [item for sublist in all_df["Genres"] for item in sublist]
set_genre = set(flat_genre)
unique_genre = list(set_genre)
#unique_genre.remove('NA')
all_df.reindex(all_df.columns.tolist() + unique_genre, axis=1, fill_value=0)

for index, row in all_df.iterrows():
    for val in row.Genres:
        all_df.loc[index, val] = 1


all_df = all_df.fillna(0)
all_df.to_csv(user_profile + ' Ratings.csv')

def jeb():
    order = ["Hyperlink", "Status", "Episodes Watched", "Episodes", "User Score", "MAL Score", "Studio"]
    jeb_df = all_df[order]
    return jeb_df

abb_df = jeb()
abb_df.to_csv(user_profile + ' Abbreviated Ratings.csv')

print("Complete!")
quit()