import requests
import json


class ArchiverConfig(object):
    """
    Interface to REST API commands supported by
    the Archiver Appliance MGMT service
    """

    def __init__(self, url):
        """
        Constructor

        Parameters
        ----------
        url : str
            url of the Archiver Appliance MGMT service

            e.g., http://xf04id-ca1.cs.nsls2.local:17665
        """
        self.url = url

    def get_all_pvs(self, regex='', limit=500):
        """
        Return all the PVs (Note this call can return millions of PVs)

        Parameters
        ----------
        regex : str, optional
            Java regex wildcard
        limit : number, optional
            number of matched PV's (default: 500)

        Returns
        -------
        list : list of PV names
        """

        params = {}

        if len(regex) != 0:
            params['pv'] = regex
            if limit != 500:
                params['limit'] = str(limit)
        else:
            if limit != 500:
                params['limit'] = str(limit)

        request_url = self.url + '/getAllPVs'

        req = requests.get(request_url, params=params, stream=True)
        result = req.json()
        return result

    def _get_pv_status(self, pvs):
        result = []
        if len(pvs) == 0:
            return result

        pv = pvs[0]
        if len(pvs) > 1:
            for pvname in pvs[1:]:
                pv += ',' + pvname

        params = {'pv': pv}
        request_url = self.url + '/getPVStatus'
        req = requests.get(request_url, params=params, stream=True)
        result = req.json()

        return result

    def get_pv_status(self, pvs):
        """
        Return the PV status

        Parameters
        ----------
        pvs : list
            list of PV names
        """
        result = []
        for i in range(0, len(pvs), 100):
            i1 = i
            i2 = min(i1+100, len(pvs))
            r = self._get_pv_status(pvs[i1: i2])
            result += r
        return result

    def get_recently_added_pvs(self):
        """
        Return a list of PVs sorted by descending PVTypeInfo creation timestamp
        """
        request_url = self.url + '/getRecentlyAddedPVs'
        req = requests.get(request_url, stream=True)
        result = req.json()
        return result

    def get_paused_pvs_report(self):
        """
        Return a list of PVs that are currently paused
        """
        request_url = self.url + '/getPausedPVsReport'
        req = requests.get(request_url, stream=True)
        result = req.json()
        return result

    def get_never_connected_pvs(self):
        """
        Return a list of PVs that have never connected
        """
        request_url = self.url + '/getNeverConnectedPVs'
        req = requests.get(request_url, stream=True)
        result = req.json()
        pvs = [pv['pvName'] for pv in result]
        return pvs

    def archive_pvs(self, pvnames):
        """
        Archive one or more PV's

        Parameters
        ----------
        pvnames : list
            list of PV names
        """
        request_url = self.url + '/archivePV'
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        pvs = []
        for pv in pvnames:
            pvdict = {}
            pvdict['pv'] = pv
            pvs.append(pvdict)

        data = json.dumps(pvs)
        req = requests.post(request_url, data=data, headers=headers)

        result = req.json()
        return result

    def _get_archiving_status(self, pvs):
        archived = []
        others = []
        if len(pvs) == 0:
            return archived, others

        pv = pvs[0]
        if len(pvs) > 1:
            for pvname in pvs[1:]:
                pv += ',' + pvname

        params = {'pv': pv}
        request_url = self.url + '/getPVStatus'
        req = requests.get(request_url, params=params, stream=True)
        result = req.json()

        for record in result:
            if record['status'] == 'Being archived':
                archived.append(record['pvName'])
            else:
                others.append(record['pvName'])
        return archived, others

    def get_archiving_status(self, pvs):
        """
        Return the PV archiving status

        Parameters
        ----------
        pvs : list
            list of PV names
        """
        archived = []
        others = []
        for i in range(0, len(pvs), 100):
            i1 = i
            i2 = min(i1+100, len(pvs))
            a, o = self._get_archiving_status(pvs[i1: i2])
            archived += a
        others += o
        return archived, others

    def abort_archiving_pv(self, pv):
        """
        Abort any pending requests for archiving this PV

        Parameters
        ----------
        pv : str
            PV name
        """
        params = {'pv': pv}
        request_url = self.url + '/abortArchivingPV'
        req = requests.get(request_url, params=params, stream=True)
        result = req.json()
        return result

    def _pause_archiving_pvs(self, pvs):
        result = []
        if len(pvs) == 0:
            return result

        pv = pvs[0]
        if len(pvs) > 1:
            for pvname in pvs[1:]:
                pv += ',' + pvname

        params = {'pv': pv}
        request_url = self.url + '/pauseArchivingPV'
        req = requests.get(request_url, params=params, stream=True)
        result = req.json()
        return result

    def pause_archiving_pvs(self, pvs):
        """
        Pause archiving the specified PVs

        Parameters
        ----------
        pvs : list
            list of PV names
        """
        pause_pvs = []
        for i in range(0, len(pvs), 100):
            i1 = i
            i2 = min(i1+100, len(pvs))
            p_pvs = self._pause_archiving_pvs(pvs[i1:i2])
            pause_pvs += p_pvs
        return pause_pvs

    def delete_pv(self, pv):
        """
        Stop archiving the specified PV (The PV needs to be paused first)

        Parameters
        ----------
        pv : str
            PV name
        """
        params = {'pv': pv}
        request_url = self.url + '/deletePV'
        req = requests.get(request_url, params=params, stream=True)
        result = req.json()
        return result
