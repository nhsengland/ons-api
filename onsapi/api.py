import copy
import json
import requests
import datetime
import itertools
from cached_property import cached_property


class DataSetMeta(object):
    def __init__(self, dataset_json, language, download_type):
        self.raw_json = dataset_json
        self.language = language
        self.download_type = download_type

    @property
    def download_links(self):
        result = []

        for document in self.raw_json["documents"]["document"]:
            if document["@type"] == self.download_type:
                href = document["href"]
                if href["@xml.lang"] == self.language:
                    result.append(href["$"])

        return result

    @property
    def publication_date(self):
        # todo make this timezone aware
        return datetime.datetime.strptime(
            self.raw_json["publicationDate"][:10], "%Y-%m-%d"
        )

    @property
    def summary(self):
        # TODO strip the html that comes in with this
        descriptions = (i["descriptions"]["description"] for i in self.raw_json["refMetadata"]["refMetadataItem"])
        chained_descriptions = itertools.chain(*descriptions)
        filtered = [i["$"] for i in chained_descriptions if i["@xml.lang"] == self.language]
        return "\n".join(filtered)


class API(object):
    """
    A simple ONS api that extracts away some of the complications

    examples usage
        api = API(your_api_key)

        -- get a list of all data set names
        api.get_data_set_names()

        -- get the specific list of hrefs for the datasets you're interested in
        api.get_data_set_details("Population Estimates for High Level Areas")

        -- get the specific list of hrefs since a certain date
        last_year = date.today() - timedelta(years=1)
        api.get_data_set_details("Population Estimates for High Level Areas", since_date=last_year)

        assumes you want everything in english, parsing results as json and the download url as csv
    """

    API_ROOT = "http://data.ons.gov.uk/ons/api/data/"

    def __init__(
        self, api_key, data_format="json", language='en', download_type="CSV"
    ):
        self.api_key = api_key
        self.data_format = data_format

        # language can equal en, or cy (for Wales)
        self.language = language
        self.download_type = download_type

    def _get_contexts(self):
        lookup = "contexts"
        content = self.query_api(lookup)
        return [i["contextName"] for i in content['contextList']["statisticalContext"]]

    @cached_property
    def all_contexts(self):
        return self._get_contexts()

    def construct_url(self, lookup):
        return "{0}{1}.{2}".format(self.API_ROOT, lookup, self.data_format)

    def query_api(self, lookup, _params=None, return_empty_404s=True):
        base_url = self.construct_url(lookup)
        if _params:
            params = copy.copy(_params)
        else:
            params = {}
        params['apikey'] = self.api_key
        result = requests.get(base_url, params=params)

        if return_empty_404s and result.status_code == 404:
            return []

        content = json.loads(result.content)

        if not result.status_code == 200:
            err_msg = 'Unable to access the api for {0} because of {1}'
            raise ValueError(err_msg, base_url, content)
        return content["ons"]


    def get_name(self, collection):
        names_list = collection["names"]["name"]
        for name in names_list:
            if name['@xml.lang'] == self.language:
                return name["$"]

    def get_data_sets(self, context, since_date=None):
        lookup = "datasets"
        params = dict(context=context)

        if since_date:
            params["from"] = since_date.strftime("%d-%m-%Y")
        result = self.query_api(lookup, params)
        if not result:
            return []
        else:
            return [i for i in result['datasetList']["contexts"]["context"]["datasets"]["dataset"]]

    def get_data_set_names(self, context=None, since_date=None):
        result = []
        contexts = self.using_contexts(context)

        for context in contexts:
            data_sets = self.get_data_sets(context, since_date)
            result.extend(self.get_name(i) for i in data_sets)

        return list(set(result))

    def using_contexts(self, context):
        if context:
            contexts = [context]
        else:
            contexts = self.all_contexts

        return contexts

    def get_data_sets_from_name(self, name, context=None, since_date=None):
        result = []
        contexts = self.using_contexts(context)
        for context in contexts:
            data_sets = self.get_data_sets(context, since_date)
            for data_set in data_sets:
                if self.get_name(data_set) == name:
                    result.append(data_set)
        return result

    def get_data_set_details(
        self, data_set_name, context=None, since_date=None
    ):
        contexts = self.using_contexts(context)
        result = []

        for context in contexts:
            data_sets = self.get_data_sets_from_name(
                data_set_name, context, since_date=since_date
            )
            for data_set in data_sets:
                query_params = dict(
                    context=context, geog=data_set["geographicalHierarchy"]
                )
                data_set_meta = self.query_api(
                    'datasetdetails/{}'.format(data_set["id"]), query_params
                )
                result.append(
                    DataSetMeta(data_set_meta["datasetDetail"], self.language, self.download_type)
                )

        return result

    def get_download_links(self, data_set_name, context=None, since_date=None):
        data_set_metas = self.get_data_set_details(data_set_name, context, since_date)
        return list(itertools.chain(*(i.download_links for i in data_set_metas)))
