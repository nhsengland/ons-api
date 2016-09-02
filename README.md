# A simple ONS api that extracts away some of the complications

example usage

```python
    api = API(your_api_key)
```

get a list of all data set names
```python
    api.get_data_set_names()
```

get the specific list of download links for the datasets you're interested in
```python
    api.get_data_set_details("Population Estimates for High Level Areas")
```

get the specific list of download links since a certain date
```python
    last_year = date.today() - timedelta(years=1)
    api.get_data_set_details("Population Estimates for High Level Areas", since_date=last_year)
```

assumes you want everything in english, parsing results as json and the download url as csv

if you wanted welsh  and the api the download type to be xls and the dataformat to be xml
you can do taht with
```python
    api = API(your_api_key, data_format='xml', language='cy', download_type='XLS')
```
