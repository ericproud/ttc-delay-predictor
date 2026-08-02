# CKAN_PACKAGE_URL/DATASET_ID live in database/ckan_client.py -- shared
# with delay_codes/, which pulls from the same CKAN package.

# CKAN resources use a hyphenated slug name for the archived year-by-year
# files (e.g. "ttc-subway-delay-data-2024"), but the current-year file uses
# a different, human-readable naming convention -- matched by exact name
# instead of the "ttc-subway-delay" + year substring check.
DATASET_SINCE_2025_NAME = "TTC Subway Delay Data since 2025.csv"

DELAY_DATA_FORMATS = ["CSV", "XLSX", "XLS"]

LINE_CODE_MAP = {
    "YU": "Line 1 (Yonge-University)",
    "YUS": "Line 1 (Yonge-University)",
    "BD": "Line 2 (Bloor-Danforth)",
    "SHP": "Line 4 (Sheppard)",
    "SHEP": "Line 4 (Sheppard)",
}

LINE_1_STATIONS = [
    "VAUGHAN METROPOLITAN CENTRE STATION",
    "HIGHWAY 407 STATION",
    "PIONEER VILLAGE STATION",
    "YORK UNIVERSITY STATION",
    "FINCH WEST STATION",
    "DOWNSVIEW PARK STATION",
    "SHEPPARD WEST STATION",
    "WILSON STATION",
    "YORKDALE STATION",
    "LAWRENCE WEST STATION",
    "GLENCAIRN STATION",
    "CEDARVALE STATION",
    "ST. CLAIR WEST STATION",
    "DUPONT STATION",
    "SPADINA STATION",
    "ST. GEORGE STATION",
    "MUSEUM STATION",
    "QUEEN'S PARK STATION",
    "ST. PATRICK STATION",
    "OSGOODE STATION",
    "ST. ANDREW STATION",
    "UNION STATION",
    "KING STATION",
    "QUEEN STATION",
    "DUNDAS STATION",
    "COLLEGE STATION",
    "WELLESLEY STATION",
    "BLOOR-YONGE STATION",
    "ROSEDALE STATION",
    "SUMMERHILL STATION",
    "ST. CLAIR STATION",
    "DAVISVILLE STATION",
    "EGLINTON STATION",
    "LAWRENCE STATION",
    "YORK MILLS STATION",
    "SHEPPARD-YONGE STATION",
    "NORTH YORK CENTRE STATION",
    "FINCH STATION",
]

LINE_2_STATIONS = [
    "KIPLING STATION",
    "ISLINGTON STATION",
    "ROYAL YORK STATION",
    "OLD MILL STATION",
    "JANE STATION",
    "RUNNYMEDE STATION",
    "HIGH PARK STATION",
    "KEELE STATION",
    "DUNDAS WEST STATION",
    "LANSDOWNE STATION",
    "DUFFERIN STATION",
    "OSSINGTON STATION",
    "CHRISTIE STATION",
    "BATHURST STATION",
    "SPADINA STATION",
    "ST. GEORGE STATION",
    "BAY STATION",
    "BLOOR-YONGE STATION",
    "SHERBOURNE STATION",
    "CASTLE FRANK STATION",
    "BROADVIEW STATION",
    "CHESTER STATION",
    "PAPE STATION",
    "DONLANDS STATION",
    "GREENWOOD STATION",
    "COXWELL STATION",
    "WOODBINE STATION",
    "MAIN STREET STATION",
    "VICTORIA PARK STATION",
    "WARDEN STATION",
    "KENNEDY STATION",
]

LINE_4_STATIONS = [
    "SHEPPARD-YONGE STATION",
    "BAYVIEW STATION",
    "BESSARION STATION",
    "LESLIE STATION",
    "DON MILLS STATION",
]

LINE_1_2_4_STATIONS = sorted(set(LINE_1_STATIONS + LINE_2_STATIONS + LINE_4_STATIONS))

LINE_STATIONS = {
    LINE_CODE_MAP["YU"].upper(): set(LINE_1_STATIONS),
    LINE_CODE_MAP["BD"].upper(): set(LINE_2_STATIONS),
    LINE_CODE_MAP["SHP"].upper(): set(LINE_4_STATIONS),
}

TARGET_DELAY_COLUMNS = [
    "date",
    "time",
    "day",
    "station",
    "line",
    "bound",
    "code",
    "vehicle",
    "min_delay",
    "min_gap",
]

VALID_BOUNDS = ["N", "S", "E", "W"]

STATION_NAME_LINE_IDENTIFIERS = [
    r"\bYONGE UNIVERSITY SPADINA\b",
    r"\bYONGE UNIVERSITY\b",
    r"\bBLOOR DANFORTH\b",
    r"\bSCARBOROUGH RT\b",
    r"\bEGLINTON CROSSTOWN\b",
    r"\bYUS\b",
    r"\bYU\b",
    r"\bBD\b",
    r"\bSRT\b",
    r"\bECLRT\b",
    r"\bLINE 1\b",
    r"\bLINE 2\b",
    r"\bLINE 3\b",
    r"\bLINE 4\b",
    r"\bLINE 5\b",
    r"\bLINE 6\b",
]

STATION_NAME_SUBSTITUTIONS = [
    (r"\bAPPRAOCHING\b|\bAPPROCHING\b", "APPROACHING"),
    (r"\bCHRSTIE\b", "CHRISTIE"),
    (r"\bKILPING\b", "KIPLING"),
    (r"\bLANDOWNE\b|\bLANDSDOWNE\b", "LANSDOWNE"),
    (r"\bLAWRECNE\b", "LAWRENCE"),
    (r"\bSHEBOURNE\b", "SHERBOURNE"),
    (r"\bISLINTON\b", "ISLINGTON"),
    (r"\bKENENDY\b|\bKENNDY\b", "KENNEDY"),
    (r"\bSCABOROUGH\b", "SCARBOROUGH"),
    (r"\bSCARB CTR\b|\bSCARB CENTRE\b", "SCARBOROUGH CENTRE"),
    (r"\bNORTH YORK CTR\b", "NORTH YORK CENTRE"),
    (r"\bEGLINTON WEST\b", "CEDARVALE"),
    (r"\bVAUGHAN MC\b|\bVMC\b", "VAUGHAN METROPOLITAN CENTRE"),
    (r"\bSTN\b|\bSTAION\b|\bSTATON\b", "STATION"),
]

STATION_NAME_NOISE_PATTERNS = [
    r"\b(APPROACHING|LEAVING|ENTERING|EXITING|DEPARTING)\b",
    r"\(.*?\)",
    r"\[.*?\]",
    r"\b(N/B|S/B|E/B|W/B|N/O|S/O|E/O|W/O|N/END|S/END|E/END|W/END)\b",
    r"\bTO\b.*",
    r"\b(PLATFORM|PLAT|TAIL TRACK|TAIL|BOOTH|BUS BAY|P1|P2|PL 1|PL 2)\b.*",
    r"\b(STATION|SUBWAY|LINE|HUB|CROSSOVER|POCKET|PORTAL)\b",
]
