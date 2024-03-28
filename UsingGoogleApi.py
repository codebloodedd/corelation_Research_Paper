import pandas as pd
from apiclient.discovery import build
from newspaper import Article
from datetime import datetime

api_key = ""

existing_df = pd.read_excel('Articles.xlsx')

df = pd.DataFrame(columns=['Date', 'Title', 'Author', 'Publication Date', 'Article Text', 'Link', 'Source URL'])

# Google Custom Search setup
query = 'Indian farmer protest'
resource = build("customsearch", 'v1', developerKey=api_key).cse()

def getArticleInfo(url, date):
    try:
        article = Article(url, timeout=10)
        article.download()

        if article.download_state != 2:
            print(f"Failed to download: {url}")
            return
        
        article.parse()
        title = article.title if article.title else None
        authors = ", ".join(article.authors) if article.authors else None
        publish_date = article.publish_date.replace(tzinfo=None) if article.publish_date else None
        text = article.text if article.text else None
        source_url = article.source_url if article.source_url else None

        df.loc[len(df)] = [date, title, authors, publish_date, text, url, source_url]
        print(url, "data added")
         
    except Exception as e:
        print(f"Error processing URL: {url}")
        print(e)

def getArticlesByDate():
    sdate = "20211101"
    edate = "20211130"
    dateRange = f"{sdate}:{edate}"
    urls = []

    for i in range(1, 100, 10):
        result = resource.list(q=query, cx='d79ec70642d91487e', sort=f"date:r:{dateRange}", start=i).execute()
        urls += result.get('items', [])

    print(len(urls))
    print(urls[0])
    for item in urls:
        url = item['link']
        # parsed_date = datetime.strptime(date, '%Y%m%d')
        # CurrDate = parsed_date.strftime('%d-%m-%Y %H:%M:%S')

# and url not in existing_df['Link'].values
        if url not in df['Link'].values:
            getArticleInfo(url, sdate)
        else:
            print("URL already processed:", url)


getArticlesByDate()

final_df = pd.concat([existing_df, df], ignore_index=True)
# final_df = df

final_df['Publication Date'] = pd.to_datetime(final_df['Publication Date'])
final_df = final_df.sort_values(by=['Publication Date'])


final_df.to_excel('Articles.xlsx', index=False)
