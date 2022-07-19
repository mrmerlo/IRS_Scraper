import requests
import lxml.html as lh
import pandas as pd

#Get Euribor and Eurirs from sole

url_euribor = "https://mutuionline.24oreborsaonline.ilsole24ore.com/guide-mutui/euribor.asp"
url_eurirs = "https://mutuionline.24oreborsaonline.ilsole24ore.com/guide-mutui/irs.asp"



def get_proper_size(l):
    
    size = l[0]
    for x in l:
        if x != size:
            size = False
            break
    return size

def get_df_from_doc(doc):

    tr_elements = doc.xpath('//tr')

    #check if every row is equal
    l = [len(T) for T in tr_elements[:12]]
    rows_ok = get_proper_size(l)

    if rows_ok: #if we got a table

        col = []
        i = 0
        for t in tr_elements[0]:
            i+=1
            name = t.text_content()
            col.append((name, []))

        for j in range(1, len(tr_elements)):
            T = tr_elements[j]
            if len(T) != rows_ok:
                break

            i = 0

            for t in T.iterchildren():
                data = t.text_content()
                col[i][1].append(data)
                i += 1

    cols_ok = get_proper_size([len(C) for (title, C) in col])
    Dict = {title:column for (title, column) in col}
    df = pd.DataFrame(Dict)
    return df

def get_EURIRS_df(doc):
    df = get_df_from_doc(doc)

    #eurirs scraping
    exp_cols = ['Descrizione', 'Fixing', 'Data', 'Fixing Pr.', 'Data Pr.']
    if all(df.columns == exp_cols):
        df.columns = ['Desc', 'Fixing', 'Date', 'Fixing-1', 'Date-1']
        #convert fixing
        df['Fixing'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing']]
        df['Fixing-1'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing-1']]
        #conver date
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        df['Date-1'] = pd.to_datetime(df['Date-1'], format="%d/%m/%Y")
        df['Desc'] = [x.replace("A", "Y") for x in df['Desc']]
        df['Maturity'] = [x.split(' ')[1] for x in df['Desc']]
        df['Settlement'] = 2
    return df

def get_EURIBOR_df(doc):
    df = get_df_from_doc(doc)
    exp_cols = ['Nome', 'Fixing', 'Data', 'Fixing Pr.', 'Data Pr.', 'Fixing 365', 'Fixing 365 Pr.']
    if all(df.columns == exp_cols):
        df.columns = ['Desc', 'Fixing', 'Date', 'Fixing-1', 'Date-1', 'Fixing365', 'Fixing365-1']

        #convert fixing
        df['Fixing'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing']]
        df['Fixing-1'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing-1']]
        df['Fixing365'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing365']]
        df['Fixing365-1'] = [float(x.replace(',', '.').replace('%', ''))/100 for x in df['Fixing365-1']]
        #conver date
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        df['Date-1'] = pd.to_datetime(df['Date-1'], format="%d/%m/%Y")
    return df

#eurirs scraping
print("EURIRS scraping...", end="")
page = requests.get(url_eurirs)
doc = lh.fromstring(page.content)
df_EURIRS = get_EURIRS_df(doc)
print("done")

#euribor scraping
page = requests.get(url_euribor)
doc = lh.fromstring(page.content)
df_EURIBOR = get_EURIBOR_df(doc)

print("Ester scraping...", end="")
#ESTER Scraping
url_ESTER = "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html"
page = requests.get(url_ESTER)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')

ester_fixing = float(tr_elements[0][1].text_content())/100
ester_date = pd.to_datetime(tr_elements[1][1].text_content(), format="%d-%m-%Y")
df_ESTER = pd.DataFrame([['ESTER', ester_fixing, ester_date]])
df_ESTER.columns = ["Desc", "Fixing", "Date"]
df_ESTER['Maturity'] = '1D'#['1d' for x in df_ESTER['Desc']]
df_ESTER['Settlement'] = 0
print("done")

#new EURIBOR SCRAPING
print("EURIBOR scraping...", end="")
url_EURIBOR = "https://www.euribor-rates.eu/en/current-euribor-rates/"
page = requests.get(url_EURIBOR)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')
tr_elements[1][1].text_content()

#EURIBOR_date = pd.to_datetime(tr_elements[1][1].text_content(), format="%d-%m-%Y")
labels = ["EURIBOR 1W", "EURIBOR 1M", "EURIBOR 3M", "EURIBOR 6M", "EURIBOR 12M"]
fixing = []
date = pd.to_datetime(tr_elements[0][1].text_content())
for i in range (0, len(labels)):  
    rate = float(tr_elements[i+1][1].text_content().replace(' %', ''))/100
    rate = round(rate, 5)
    fixing.append(rate)
    
df_EURIBOR = pd.DataFrame(list(zip(labels, fixing, [date for x in labels])))
df_EURIBOR.columns = ["Desc", "Fixing", "Date"]
df_EURIBOR['Settlement'] = 2
df_EURIBOR['Maturity'] = [x.split(" ")[1] for x in df_EURIBOR['Desc']]
print("Done")

#last
selection = ['Date', 'Fixing', 'Desc', 'Maturity', 'Settlement']
df_ESTER = df_ESTER[selection].copy()
df_EURIBOR = df_EURIBOR[selection].copy()
df_EURIRS = df_EURIRS[selection].copy()

print("Market Data has been downloaded...")