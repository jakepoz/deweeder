import requests

class NtripClient:
    def __init__(self, caster, user, password, mountpoint, port=2101) -> None:
        self.caster = caster
        self.user = user
        self.password = password
        self.mountpoint = mountpoint
        self.port = port

    def run(self):
        req = requests.Request("GET", 
                                url=f"http://{self.caster}:{self.port}/{self.mountpoint}",
                                headers={
                                    "Ntrip-Version": "Ntrip/2.0",
                                    "User-Agent": "NTRIP deweederbot/1.0"
                                },
                                auth=(self.user, self.password))

        r = req.prepare()
        s = requests.Session()
        res = s.send(r, stream=True)

        assert res.status_code == 200

        for data in res.iter_content():
            print(data)
