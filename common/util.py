def dict_list_reduce(d, key):
    data = []
    for i in d:
        data.append(i[key])
    return data
    
def get_date():
    return datetime.datetime.strftime(datetime.datetime.now(), "%y-%m-%d %H:%M:%S")