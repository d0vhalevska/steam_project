import numpy as np
import pandas as pd
import os
import glob
import ntpath
ntpath.basename("a/b/c")

datasets_path = "./datasets"
plots_path = "./plots"
output_datasets = "./datasets/generated"
genres_file = "applicationTags.csv"
genres_out = "genre_id.csv"

def get_genres(save = True):
    """
    Read Tags from csv

    Arguments
    ----------
    save : boolean : save csv with dataset or not
        default True

    Return
    ----------
    DataFrame in format [genre, id]

    Raised Exceptions
    ----------

    Side Effects
    ----------

    """
    csv = open('{}/{}'.format(datasets_path, genres_file), 'r')
    df = pd.DataFrame(columns=["genre", "id"])


    for line in csv:
        row = line.strip().split(',')
        id = row[0]
        for i in range(1,len(row)):
            tag = row[i]
            to_append = [tag, id]
            series = pd.Series(to_append, index=df.columns)
            df = df.append(series,ignore_index=True)

    if save:
        df.to_csv('{}/{}'.format(output_datasets, genres_out), sep=',',index=False)
    return df

def path_leaf(path):
    """
    Gets filename without extension from whole path
    (UNIX only, not sure if it works with DOS paths)
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
def get_counts(period = ['year'], save = True):
    """
    Read historical player counts from CSVs

    Arguments
    ----------
    period : list containing time periods to group by and calculate mean
        default ['year']
    save : boolean : save csv?
        default TRUE, it really takes long to calculate them :c

    Return
    ----------
    DataFrame in format [id, count, (year, month, day)]

    Raised Exceptions
    ----------

    Side Effects
    ----------

    """
    # use glob to get all the csv files 
    # in the folder
    counts_folder = "/PlayerCountHistory"
    csv_files = glob.glob(os.path.join(datasets_path + counts_folder, "*.csv"))
    
    game_df = pd.DataFrame(columns = ['id', 'count'] + period)

    # loop over the list of csv files
    for f in csv_files:
        appdata = str((path_leaf(f).split('.'))[-2])
        # read the csv file
        df = pd.read_csv(f)
        df.rename(columns = {'Time':'DateTime', 'Playercount':'count'},inplace=True)
        date = pd.to_datetime(df['DateTime'])
        df["year"] = date.dt.year
        df["month"] = date.dt.month
        df["day"] = date.dt.day
        df = df.drop(columns=['DateTime'])
        df = df.drop(columns=[i for i in ['year','month','day'] if i not in period])
        df = df.groupby(period).mean().reset_index()
        df['id'] = appdata
        game_df = pd.concat([game_df,df], ignore_index=True)
    for i in period:
        game_df[i] = game_df[i].astype('int')
    if save:
        game_df.to_csv(output_datasets + "/player_count_" + (period[-1] + 'ly.csv' if len(period)>0 else 'total.csv'), index = False)
    return game_df

def merge_genres_counts(genres, counts, period = ['year'], save = True):
    """
    Merge genres and counts to one dataframe containing genres playcounts

    Arguments:
    genres : df [genre, id]
    period : list containing time periods to group by and calculate mean
        default ['year']
    counts : df [id, count, (year, month, day)]
    save : boolean : save csv?
        default True

    Return:
    DataFrame in format [genre, count, (year, month, day)]

    Raised Exceptions
    ----------

    Side Effects
    ----------

    """

    df = pd.merge(genres,counts,how='inner', on=['id'])
    df = df.drop(columns=['id'])
    df = df.groupby(["genre"]+ period).mean().reset_index()
    
    if save:
        df.to_csv(output_datasets + "/genres_count_" + (period[-1] + 'ly.csv' if len(period)>0 else 'total.csv'), index=False)
    return df
def get_prices(period = ['year'], save = True):
    """
    Read historical prices from CSVs

    Arguments
    ----------
    period : list containing time periods to group by and calculate mean
        default ['year']
    save : boolean : save csv?
        default TRUE

    Return
    ----------
    DataFrame in format [id, initialprice, finalprice, discount, (year, month, day)]

    Raised Exceptions
    ----------

    Side Effects
    ----------

    """
    # use glob to get all the csv files 
    # in the folder
    prices_folder = "/PriceHistory"
    csv_files = glob.glob(os.path.join(datasets_path + prices_folder, "*.csv"))
    
    prices = pd.DataFrame(columns = ['id','initialprice','finalprice','discount'] + period)

    # loop over the list of csv files
    for f in csv_files:
        appdata = str((path_leaf(f).split('.'))[-2])
        # read the csv file
        df = pd.read_csv(f)
        df.rename(columns = {'Date':'DateTime', 'Playercount':'count'},inplace=True)
        date = pd.to_datetime(df['DateTime'])
        df["year"] = date.dt.year
        df["month"] = date.dt.month
        df["day"] = date.dt.day
        df = df.drop(columns=['DateTime'])
        df = df.drop(columns=[i for i in ['year','month','day'] if i not in period])
        df = df.groupby(period).mean().reset_index()
        df.rename(columns={'Initialprice':'initialprice','Finalprice':'finalprice','Discount':'discount'}, inplace = True)
        df['id'] = appdata
        prices = pd.concat([prices,df], ignore_index=True)
    for i in period:
        prices[i] = prices[i].astype('int')
    if save:
        prices.to_csv(output_datasets + "/prices_" + (period[-1] + 'ly.csv' if len(period)>0 else 'total.csv'), index = False)
    return prices

def merge_prices_counts(prices, counts, period = ['year'], save = True):
    """
    Merge prices and counts to one dataframe containing games prices and playcounts

    Arguments
    ----------
    genres : df [genre, id]
    period : list containing time periods to group by and calculate mean
        default ['year']
    counts : df [id, count, (year, month, day)]
    save : boolean : save csv?
        default True

    Return
    ----------
    DataFrame in format [id, initialprice, finalprice, discount, count, (year, month, day)]

    Raised Exceptions
    ----------
    -

    Side Effects
    ----------
    Initial prise is maximized (which actually does nothing, it is constant for a game? hopefully)
    Final price is minimized and discount maximized giving the most maximum discount in given period. 
    Counts are mean over given period.
    Period is "total" if none given.

    """
    df = pd.merge(prices,counts,how='inner', on=['id', 'year'])
    df = df.groupby(["id"]+ period).agg({'initialprice':'max','finalprice':'min','discount':'max','count':'mean'}).reset_index()
    df = df[['id','initialprice','finalprice','discount','count']+period]
    if save:
        df.to_csv(output_datasets + "/prices_count_" + (period[-1] + 'ly.csv' if len(period)>0 else 'total.csv'), index=False)
    return df

if __name__ == "__main__":
    period = ['year','month']
    save = True

    ### Genres - Id dataset
    get_genres(save)
    genres = pd.read_csv(output_datasets + "/genre_id.csv")
    # print(genres)

    ### Player counts
    get_counts(period, save)
    counts = pd.read_csv(output_datasets + "/player_count_monthly.csv")
    # print(counts)

    ### Prices
    get_prices(['year','month'])
    prices = pd.read_csv(output_datasets + "/prices_monthly.csv")
    # print(prices)

    ### Game Price Cout all together. Already contains everything neaded for plot (3)
    # merge_prices_counts(prices, counts, period = [])
    # prices_counts = pd.read_csv(output_datasets + "/prices_count_total.csv")
    # print(prices_counts)

    ### Genres - counts
    merge_genres_counts(genres, counts, period, save)
    genres_counts = pd.read_csv(output_datasets + "/genres_count_monthly.csv")
    # print(genres_counts)
    
    ### Create overall top-12 genres (mean from monthly dataset)
    top_12 = genres_counts.groupby('genre').mean().reset_index().sort_values('count', ascending = False)[0:12].drop(columns=['year','month'])
    top_12.to_csv(output_datasets+"/genres_count_overall_top_12.csv", index = False)
    top_12 = pd.read_csv(output_datasets+"/genres_count_overall_top_12.csv")

    ## Create monthly top-12 bla bla
    genres_counts[genres_counts.genre.isin(top_12.genre)].to_csv(output_datasets + "/genres_count_monthly_top_12.csv", index=False)

    ### Prices of games with top 12 Genres
    # prices_counts[prices_counts.id.isin(genres[genres.genre.isin(top_12.genre)].id)].to_csv(output_datasets + "/prices_count_total_top_12.csv", index=False)

    

    ### Makes (2) 2017 and 2020 mean player counts for top_12 genres
    # genres_counts[(genres_counts.genre.isin(top_12.genre))&
    #     ((genres_counts.year == 2017) | (genres_counts.year == 2020))].to_csv(output_datasets+"/genres_count_2017_2020.csv", index = False)


    

    