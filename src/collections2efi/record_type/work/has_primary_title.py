from collections2efi.record import XMLAccessor
from collections2efi.record_type.work.utils import compute_title


def has_primary_title(xml: XMLAccessor):
    return compute_title(xml)[0]
