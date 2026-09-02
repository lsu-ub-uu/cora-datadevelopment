import xml.etree.ElementTree as ET

from cora.validate import _create_validation_order


def test_create_validation_order():
    record = ET.fromstring(
        "<diva-output><recordInfo><id>123</id></recordInfo></diva-output>"
    )

    work_order = _create_validation_order("diva-output", record)

    assert (
        work_order.findtext(
            "./order/validationOrder/recordInfo/dataDivider/linkedRecordType"
        )
        == "system"
    )
    assert (
        work_order.findtext(
            "./order/validationOrder/recordInfo/dataDivider/linkedRecordId"
        )
        == "divaData"
    )
    assert (
        work_order.findtext(
            "./order/validationOrder/recordInfo/validationType/linkedRecordType"
        )
        == "validationType"
    )
    assert (
        work_order.findtext(
            "./order/validationOrder/recordInfo/validationType/linkedRecordId"
        )
        == "validationOrder"
    )
    assert (
        work_order.findtext("./order/validationOrder/recordType/linkedRecordType")
        == "recordType"
    )
    assert (
        work_order.findtext("./order/validationOrder/recordType/linkedRecordId")
        == "diva-output"
    )
    assert work_order.findtext("./order/validationOrder/validateLinks") == "false"
    assert work_order.findtext("./order/validationOrder/metadataToValidate") == "new"
    assert work_order.find("./record/diva-output") is record
