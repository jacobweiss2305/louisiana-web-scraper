from datetime import datetime, timedelta
import pandas as pd

def create_dateframe(n_years, format):
    today = datetime.today()
    start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=365 * n_years)

    dates = []
    while start_date <= today:
        end_date = start_date.replace(day=1, hour=23, minute=59, second=59, microsecond=999) + timedelta(days=32)
        end_date = end_date - timedelta(days=end_date.day)
        dates.append((start_date.strftime(format), end_date.strftime(format)))
        start_date = end_date + timedelta(days=1)

    df = pd.DataFrame(dates, columns=['Effective Date', 'To Date'])
    return df
