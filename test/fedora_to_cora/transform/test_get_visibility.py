import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_visibility import get_visibility


def test_return_published_when_last_update_is_published():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UNPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>PUBLISHED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "published"


def test_return_published_when_autopublished():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "published"


def test_return_unpublished_when_last_update_unpublished():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UPDATED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UNPUBLISHED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "unpublished"


def test_return_unpublished_when_last_update_deleted():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>DELETED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "unpublished"


def test_ignores_updated_actions():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UNPUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>PUBLISHED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UPDATED</userAction>
                </userInformation>
                <userInformation>
                    <userAction>UPDATED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "published"


def test_return_published_when_no_updaters_but_creator_info_has_userAction_created():
    fedora_xml = """
    <publication>
        <administrativeInfo>
            <creatorInfo>
                <userId>test.testsson@domain.se</userId>
                <ip>111.111.11.11</ip>
                <name>Test Testsson</name>
                <date>2022-10-13T15:25:08.480+02:00</date>
                <userType>DOMAINADMIN</userType>
                <userAction>CREATED</userAction>
            </creatorInfo>
        </administrativeInfo>
    </publication>
    """
    assert get_visibility(ET.fromstring(fedora_xml)) == "published"
