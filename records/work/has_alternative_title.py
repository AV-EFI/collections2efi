from records.record import XMLAccessor
from records.work.utils import compute_title


def has_alternative_title(xml: XMLAccessor):
    return compute_title(xml)[1:]
