import xml.etree.ElementTree as ET
from fedora_to_cora.create_related_item_type_series import (
    create_related_item_type_series,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_create_controlled_series_link(monkeypatch):
    series_old_id_1 = "17450"
    series_old_id_2 = "17451"
    series_cora_id_1 = "diva-series:17450"
    series_cora_id_2 = "diva-series:17451"

    def get_cora_id_by_old_id_mock(old_id, *args, **kwargs):
        if old_id == series_old_id_1:
            return series_cora_id_1
        elif old_id == series_old_id_2:
            return series_cora_id_2
        else:
            raise ValueError(f"Unexpected old ID: {old_id}")

    monkeypatch.setattr(
        "fedora_to_cora.create_related_item_type_series.get_cora_id_by_old_id",
        get_cora_id_by_old_id_mock,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <seriesInfos>
                <seriesInfo>
                    <series>
                        <seriesId>{series_old_id_1}</seriesId>
                    </series>
                </seriesInfo>
                <seriesInfo>
                    <series>
                        <seriesId>{series_old_id_2}</seriesId>
                    </series>
                </seriesInfo>
            </seriesInfos>
        </publication>
        """
    )

    series_items = create_related_item_type_series(source_record, MockContext())

    assert len(series_items) == 2
    assert_equal_for_xml_and_xml_string(
        series_items[0],
        f"""
        <relatedItem type="series" repeatId="controlled0">
            <series>
                <linkedRecordType>diva-series</linkedRecordType>
                <linkedRecordId>{series_cora_id_1}</linkedRecordId>
            </series>
        </relatedItem>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        series_items[1],
        f"""
        <relatedItem type="series" repeatId="controlled1">
            <series>
                <linkedRecordType>diva-series</linkedRecordType>
                <linkedRecordId>{series_cora_id_2}</linkedRecordId>
            </series>
        </relatedItem>
        """,
    )


def test_create_uncontrolled_series():
    source_record = ET.fromstring(
        """
        <publication>
            <uncontrolledSeriesInfo>
                <series>
                    <issn>4444-5555</issn>
                    <eissn>6666-7777</eissn>
                    <seriesNameUncontrolled>Okontrollerad serie</seriesNameUncontrolled>
                    <controlled>false</controlled>
                </series>
                <numberInSeries>66</numberInSeries>
            </uncontrolledSeriesInfo>
        </publication>
        """
    )
    series = create_related_item_type_series(source_record, MockContext())

    assert len(series) == 1
    assert_equal_for_xml_and_xml_string(
        series[0],
        """
         <relatedItem type="series" repeatId="uncontrolled0">
            <titleInfo>
                <title>Okontrollerad serie</title>
            </titleInfo>
            <identifier type="issn" displayLabel="pissn">4444-5555</identifier>
            <identifier type="issn" displayLabel="eissn">6666-7777</identifier>
            <partNumber>66</partNumber>
        </relatedItem>
        """,
    )


def xtest_creates_controlled_and_uncontrolled_series(monkeypatch):
    series_old_id_1 = "17450"
    series_old_id_2 = "17451"
    series_cora_id_1 = "diva-series:17450"
    series_cora_id_2 = "diva-series:17451"

    def get_cora_id_by_old_id_mock(old_id, *args, **kwargs):
        if old_id == series_old_id_1:
            return series_cora_id_1
        elif old_id == series_old_id_2:
            return series_cora_id_2
        else:
            raise ValueError(f"Unexpected old ID: {old_id}")

    monkeypatch.setattr(
        "fedora_to_cora.create_related_item_type_series.get_cora_id_by_old_id",
        get_cora_id_by_old_id_mock,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <seriesInfos>
                <seriesInfo>
                    <series>
                        <seriesId>{series_old_id_1}</seriesId>
                    </series>
                </seriesInfo>
                <uncontrolledSeriesInfo>
                    <series>
                        <seriesNameUncontrolled>Okontrollerad serie</seriesNameUncontrolled>
                    </series>
                </uncontrolledSeriesInfo>
            </seriesInfos>
        </publication>
        """
    )

    series_items = create_related_item_type_series(source_record, MockContext())

    assert len(series_items) == 2
    assert_equal_for_xml_and_xml_string(
        series_items[0],
        """
        <relatedItem type="series" repeatId="controlled0">
            <series>
                <linkedRecordType>diva-series</linkedRecordType>
                <linkedRecordId>diva-series:17450</linkedRecordId>
            </series>
        </relatedItem>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        series_items[1],
        """
         <relatedItem type="series" repeatId="uncontrolled0">
            <titleInfo>
                <title>Okontrollerad serie</title>
            </titleInfo>
        </relatedItem>
        """,
    )
