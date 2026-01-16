from cora.get_deployment_info import get_deployment_info


def test_get_deployment_info(requests_mock):
    requests_mock.get(
        "https://preview.diva.cora.epc.ub.uu.se/rest/",
        headers={"Accept": "application/vnd.cora.deploymentInfo+json"},
        json=mock_deployment_info,
    )

    deployment_info = get_deployment_info("preview")
    deployment_info == mock_deployment_info


mock_deployment_info = {
    "applicationName": "diva",
    "deploymentName": "DiVA - example deployment",
    "coraVersion": "3.2.0",
    "applicationVersion": "1.16.0",
    "urls": {
        "REST": "http://192.168.49.2:30982/rest/",
        "appTokenLogin": "http://192.168.49.2:30982/login/rest/apptoken",
        "passwordLogin": "http://192.168.49.2:30982/login/rest/password",
        "record": "http://192.168.49.2:30982/rest/record/",
        "recordType": "http://192.168.49.2:30982/rest/record/recordType",
        "iiif": "http://192.168.49.2:30982/iiif/",
    },
    "exampleUsers": [
        {
            "name": "domainAdmin UU",
            "text": "Apptoken, coraUser:491144693381458",
            "type": "appTokenLogin",
            "loginId": "dominAdminUU@diva.cora.uu.se",
            "appToken": "5f565f47-761d-4a16-8fca-6cd4e1955fc2",
        },
        {
            "name": "SystemOne Admin",
            "text": "Apptoken, 141414",
            "type": "appTokenLogin",
            "loginId": "systemoneAdmin@system.cora.uu.se",
            "appToken": "aaaaa-aaa-aaa-aaaa-aaaaaaa",
        },
        {
            "name": "admin Nordiska Museet",
            "text": "Apptoken, user:182924359788077",
            "type": "appTokenLogin",
            "loginId": "adminNordiskaMuseet@diva.cora.uu.se",
            "appToken": "bbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb",
        },
        {
            "name": "DiVA SystemAdmin",
            "text": "Apptoken, 161616",
            "type": "appTokenLogin",
            "loginId": "divaAdmin@cora.epc.ub.uu.se",
            "appToken": "cccccc-cccc-cccc-cccc-ccccccccccc",
        },
    ],
}
