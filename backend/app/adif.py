from app.models import QSO


def _adif_field(name: str, value: str) -> str:
    return f"<{name}:{len(value)}>{value}"


def generate_adif(operator_callsign: str, qsos: list[QSO]) -> str:
    lines = []

    # Header
    lines.append(_adif_field("ADIF_VER", "3.1.4"))
    lines.append(_adif_field("PROGRAMID", "POTA Logger"))
    lines.append(
        _adif_field("PROGRAMVERSION", "1.0")
    )
    lines.append("<EOH>")
    lines.append("")

    for qso in qsos:
        record = []
        record.append(_adif_field("STATION_CALLSIGN", operator_callsign.upper()))
        record.append(_adif_field("CALL", qso.callsign.upper()))
        record.append(_adif_field("SIG", "POTA"))
        record.append(_adif_field("SIG_INFO", qso.park_reference.upper()))
        record.append(_adif_field("QSO_DATE", qso.timestamp.strftime("%Y%m%d")))
        record.append(_adif_field("TIME_ON", qso.timestamp.strftime("%H%M%S")))
        record.append(_adif_field("BAND", qso.band.lower()))
        freq_str = f"{float(qso.frequency):.4f}"
        record.append(_adif_field("FREQ", freq_str))
        record.append(_adif_field("MODE", qso.mode.upper()))
        record.append(_adif_field("RST_SENT", qso.rst_sent))
        record.append(_adif_field("RST_RCVD", qso.rst_received))
        record.append("<EOR>")
        lines.append(" ".join(record))
        lines.append("")

    return "\n".join(lines)
