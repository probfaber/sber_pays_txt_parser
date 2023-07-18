import os.path
import datetime
import re
from glob import glob
import pandas as pd


FIELDS = {
    "code_1": {
        "caption": "Код ГОСБ сбербанка",
        "type": "str",
        "extract_pattern": r"^([^;]+)",
    },
    "code_2": {
        "caption": "Код подразделения банка",
        "type": "str",
        "extract_pattern": r"^[^;]*;([^;]+)",
    },
    "account_no":
    {
        "caption": "№ клиента",
        "type": "str",
        "required": True,
        "extract_pattern": r";\s*CLIENTNO\s*:\s*([^;]+)",
    },
    "payment_date": {
        "caption": "Дата",
        "type": "date",
        "extract_pattern": r";\s*(\d{2}/\d{2}/\d{4})\s*;",
    },
    "method_pay": {
        "caption": "Способ совершения платежа",
        "type": "str",
        "extract_pattern": r";\s*method_pay\s*:\s*([^;]*)",
    },
    "summ_pay": {
        "caption": "Сумма платежа",
        "type": "float",
        "extract_pattern": r"^" + r"[^;]*;" * 4 + r"\s*([\d\.]+)",
    },
    "summ_fee_from_receiver": {
        "caption": "Комиссия с получателя",
        "type": "float",
        "extract_pattern": r"^" + r"[^;]*;" * 5 + r"\s*([\d\.]+)",
    },
    "num_ipd": {
        "caption": "Номер ИПД",
        "type": "str",
        "extract_pattern": r";\s*CLIENTDOCNO\s*:\s*([^;]*)",
    },
    "val_count": {
        "caption": "Передано показаний",
        "type": "int",
        "extract_pattern": r";\s*CounterVal_\d+\s*:\s*(\d+(?:[\.,]\d*)?)",
    },
}

EMPTY_FIELDS_ROW = dict([(x, None) for x in FIELDS.keys()])


def parse_file(data_file):
    with open(data_file, "r", encoding="cp1251") as f:
        lines = [line.rstrip("\n").strip() for line in f]

    rows = []

    for line in lines:
        item = EMPTY_FIELDS_ROW.copy()
        good_line = True
        # сначала обычные поля
        for field in [key for key in FIELDS.keys() if key != "val_count"]:
            ptn = FIELDS[field]["extract_pattern"]
            m = re.search(ptn, line, re.IGNORECASE)
            if m:
                item[field] = m.group(1)
            # без этого поля не брать строку
            if FIELDS[field].get("required", False):
                good_line = good_line and item[field]
            if not good_line:
                break
        if not good_line:
            continue
        # подсчет показаний
        field = "val_count"
        ptn = FIELDS[field]["extract_pattern"]
        m_list = re.findall(ptn, line, re.IGNORECASE)
        if m_list:
            item[field] = len(m_list)
        else:
            item[field] = 0

        rows.append(item)
    return rows


def main(data_path, out_path):
    data_name = os.path.basename(data_path)
    time_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file_name = "{}_{}".format(data_name, time_str)
    out_file = os.path.join(out_path, out_file_name) + '.xlsx'

    rows = []
    print("обработка...")

    # get files
    recursive = True
    lst = []
    for mask in ('*.txt',):
        if recursive:
            search_path = os.path.join(data_path, '**', mask)
        else:
            search_path = os.path.join(data_path, mask)
        lst.extend(glob(search_path, recursive=recursive))
    lst = list(set(lst))
    lst = [x for x in lst if os.path.isfile(x)]

    for data_file in lst:
        file_name = os.path.basename(data_file)
        parsed_rows = parse_file(data_file)
        # если файл кривой, то все равно его в список
        if len(parsed_rows) == 0:
            parsed_rows = [EMPTY_FIELDS_ROW.copy(), ]
        # добавить имя файла
        for item in parsed_rows:
            item["file"] = file_name

        rows.extend(parsed_rows)

    df_cols = ["file"] + [x for x in FIELDS.keys()]
    df_col_captions = ["Файл"] + [x["caption"] for _, x in FIELDS.items()]

    df = pd.DataFrame(rows, columns=df_cols)

    for k in FIELDS.keys():
        t = FIELDS[k].get('type', 'str')
        if t == 'date':
            df[k] = pd.to_datetime(df[k], format="%d/%m/%Y", errors='coerce').dt.date
        elif t == 'float':
            df[k] = df[k].astype(float)
        elif t == 'int':
            df[k] = pd.to_numeric(df[k], 'coerce').fillna(0).astype(int)

    # print(df)
    print("выгрузка...")

    with pd.ExcelWriter(
        out_file, date_format="dd.mm.yyyy", datetime_format="dd.mm.yyyy hh:mm:ss"
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            header=df_col_captions,
            float_format="%.2f",
            sheet_name="Лист1",
        )

    print("завершено")


if __name__ == "__main__":
    data_path = r"C:\work\_py_projects\сбербанка платежки показания 2020-04-22\data\реестры"
    out_path = r"C:\work\_py_projects\сбербанка платежки показания 2020-04-22\result"

    main(data_path, out_path)
