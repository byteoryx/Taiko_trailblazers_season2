import json

from datatypes.rhino import RhinoContractsResponse
from tools.session import get_proxied_session


def get_deployed_contracts(address: str, proxy: str) -> RhinoContractsResponse:
    try:
        url = "https://api.rhino.fi/contract-interactions/contracts/TAIKO?" \
              "sortBy=latest&" \
              "limit=100&" \
              "skip=0&" \
              f"deployer={address.lower()}"
        response = get_proxied_session(proxy=proxy, headers_update=False).get(url=url)
        return RhinoContractsResponse.parse_obj(json.loads(response.content))
    except:
        pass
