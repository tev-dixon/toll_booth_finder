import openpyxl
from typing import List, Optional



class RowData:
    def __init__(self, ID: Optional[int], Color: Optional[str], origin: Optional[str], destination: Optional[str], 
                 City1: Optional[str], City2: Optional[str], City3: Optional[str], City4: Optional[str], 
                 Highway1: Optional[str], Highway2: Optional[str], Highway3: Optional[str], Highway4: Optional[str], 
                 q_8_8_state_1: Optional[str]):
        self.ID = ID
        self.Color = Color
        self.origin = origin
        self.destination = destination
        self.City1 = City1
        self.City2 = City2
        self.City3 = City3
        self.City4 = City4
        self.Highway1 = Highway1
        self.Highway2 = Highway2
        self.Highway3 = Highway3
        self.Highway4 = Highway4
        self.q_8_8_state_1 = q_8_8_state_1

def read_first_13_columns(file_name: str) -> List[RowData]:
    workbook = openpyxl.load_workbook(file_name)
    sheet = workbook.active
    data = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        rowData = RowData(
            ID=row[0], Color=row[1], origin=row[2], destination=row[3],
            City1=row[4], City2=row[5], City3=row[6], City4=row[7],
            Highway1=row[8], Highway2=row[9], Highway3=row[10], Highway4=row[11],
            q_8_8_state_1=row[12]
        )
        data.append(rowData)

    return data

file_name = "Book.xlsx"
data = read_first_13_columns(file_name)

# Display the data
for row in data:
    print(row.__dict__)


