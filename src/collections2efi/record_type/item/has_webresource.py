from collections2efi.record import XMLAccessor


def has_webresource(xml: XMLAccessor):
    uri = (
        "https://sammlungen.deutsche-kinemathek.de/recherche/itemdetails/sdk"
        + xml.xpath("@priref")[0]
    )
    return [uri]
