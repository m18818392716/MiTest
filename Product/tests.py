def getWeek(n=0):
    from datetime import datetime, timedelta
    now = datetime.now()
    if n < 0:
        return datetime(now.year, now.month, now.day)
    else:
        oldData = now - timedelta(days=n * 1)
        return datetime(oldData.year, oldData.month, oldData.day)


days = [getWeek(x) for x in [6, 5, 4, 3, 2, 1, 0]];
for day in days:
    print(day)



