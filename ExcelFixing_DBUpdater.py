import pandas as pd

def get_reshaped_record(record):

    dates = set(record['Date'])
    descs = record['Desc']
    record = record.set_index(['Date','Desc'])
    data = []
    for d in dates:
        row = [d]
        for desc in descs:
            if (d, desc) in record.index:
                row.append(record.loc[d, desc]['Fixing'])
            else:
                row.append(-1)
        data.append(row)
    cols = ['DATE'] + list(descs)
    new_df = pd.DataFrame(data, columns = cols )
    new_df = new_df.set_index('DATE')
    return new_df

def update_history(history, new_record):
    for d in new_record.index:
        for rate in new_record.columns:
            if new_record.at[d, rate] != -1:
                history.at[d, rate] = new_record.at[d, rate]
    history.fillna(-1, inplace=True)

if __name__ == "__main__":
    exec(open("EuriborEurirsScraper.py").read())
    record = pd.concat([df_ESTER, df_EURIBOR, df_EURIRS]).reset_index(drop=True)

    excel_name = 'fixings.xlsx'
    sheet = "fixing_history"


    new_record = get_reshaped_record(record)
    print("opening excel file ", excel_name)
    history = pd.read_excel('fixings.xlsx')
    history = history.set_index('DATE')
    update_history(history, new_record)
    print("Updating excel file ", excel_name, "...", end="")

    with pd.ExcelWriter(excel_name, date_format = 'yyyy-mm-dd', datetime_format = 'yyyy-mm-dd') as writer:
        history.sort_index(ascending = False).to_excel(writer, sheet_name = sheet, index=True )
    print("Done")
